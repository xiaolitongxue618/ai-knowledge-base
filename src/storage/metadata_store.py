"""
元数据存储模块（SQLite）
"""

import sqlite3
from typing import Optional, List
from pathlib import Path

from src.models.document import Document, DocumentStatus
from src.utils.logger import logger


class MetadataStore:
    """SQLite 元数据存储管理器"""

    def __init__(self, db_path: str = "./data/metadata/knowledge_base.db"):
        """
        初始化元数据存储

        Args:
            db_path: 数据库文件路径，":memory:" 表示内存模式
        """
        self.db_path = db_path
        self.is_memory_mode = (db_path == ":memory:")

        # 内存模式：保持连接打开
        if self.is_memory_mode:
            self.conn = sqlite3.connect(":memory:")
            self._init_db_cursor(self.conn.cursor())
            self.conn.commit()
            logger.info("元数据存储初始化: 内存模式")
        else:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._init_db()

    def _get_connection(self):
        """获取数据库连接"""
        if self.is_memory_mode:
            return self.conn
        else:
            return sqlite3.connect(self.db_path)

    def _init_db_cursor(self, cursor):
        """使用游标初始化数据库表"""
        # 创建文档表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'indexing',
                chunk_count INTEGER DEFAULT 0,
                error_message TEXT,
                file_path TEXT
            )
        """)

        # 创建问答历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_id
            ON documents(source_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status
            ON documents(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_timestamp
            ON chat_history(timestamp DESC)
        """)

    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            self._init_db_cursor(cursor)
            conn.commit()
            logger.info(f"元数据存储初始化完成: {self.db_path}")
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
            raise
        finally:
            conn.close()

    def create_document(
        self,
        source_id: str,
        file_name: str,
        file_type: str,
        file_size: int,
        file_path: Optional[str] = None
    ) -> bool:
        """
        创建新文档记录（状态为 indexing）

        Args:
            source_id: 文件 MD5 哈希
            file_name: 文件名
            file_type: 文件类型（pdf/md/txt）
            file_size: 文件大小（字节）
            file_path: 文件路径

        Returns:
            bool: 是否创建成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO documents
                (source_id, file_name, file_type, file_size, file_path, status)
                VALUES (?, ?, ?, ?, ?, 'indexing')
            """, (source_id, file_name, file_type, file_size, file_path))

            conn.commit()

            if not self.is_memory_mode:
                conn.close()

            logger.info(f"创建文档记录: {source_id} ({file_name})")
            return True

        except sqlite3.IntegrityError:
            logger.warning(f"文档已存在: {source_id}")
            return False
        except Exception as e:
            logger.error(f"创建文档失败: {e}")
            return False

    def get_document(self, source_id: str) -> Optional[Document]:
        """
        获取文档记录

        Args:
            source_id: 文档 source_id

        Returns:
            Document: 文档对象，不存在返回 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT source_id, file_name, file_type, file_size,
                   status, chunk_count, error_message, file_path
            FROM documents
            WHERE source_id = ?
        """, (source_id,))

        row = cursor.fetchone()

        if not self.is_memory_mode:
            conn.close()

        if row:
            return Document(
                source_id=row[0],
                file_name=row[1],
                file_type=row[2],
                file_size=row[3],
                status=DocumentStatus(row[4]),
                chunk_count=row[5],
                error_message=row[6],
                file_path=row[7]
            )
        return None

    def update_status(
        self,
        source_id: str,
        status: DocumentStatus,
        chunk_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        更新文档状态

        Args:
            source_id: 文档 source_id
            status: 新状态
            chunk_count: 块数量（仅 active 需要）
            error_message: 错误信息（仅 failed 需要）

        Returns:
            bool: 是否更新成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if status == DocumentStatus.FAILED:
                cursor.execute("""
                    UPDATE documents
                    SET status = ?, error_message = ?
                    WHERE source_id = ?
                """, (status.value, error_message, source_id))

            elif status == DocumentStatus.ACTIVE:
                cursor.execute("""
                    UPDATE documents
                    SET status = ?, chunk_count = ?
                    WHERE source_id = ?
                """, (status.value, chunk_count, source_id))

            elif status == DocumentStatus.INDEXING:
                cursor.execute("""
                    UPDATE documents
                    SET status = ?, error_message = NULL
                    WHERE source_id = ?
                """, (status.value, source_id))

            conn.commit()

            if not self.is_memory_mode:
                conn.close()

            logger.info(f"更新文档状态: {source_id} -> {status.value}")
            return True

        except Exception as e:
            logger.error(f"更新状态失败: {e}")
            return False

    def list_documents(
        self,
        status: Optional[DocumentStatus] = None
    ) -> List[Document]:
        """
        列出所有文档

        Args:
            status: 过滤状态（可选）

        Returns:
            List[Document]: 文档列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("""
                SELECT source_id, file_name, file_type, file_size,
                       status, chunk_count, error_message, file_path
                FROM documents
                WHERE status = ?
                ORDER BY upload_time DESC
            """, (status.value,))
        else:
            cursor.execute("""
                SELECT source_id, file_name, file_type, file_size,
                       status, chunk_count, error_message, file_path
                FROM documents
                ORDER BY upload_time DESC
            """)

        rows = cursor.fetchall()

        if not self.is_memory_mode:
            conn.close()

        return [
            Document(
                source_id=row[0],
                file_name=row[1],
                file_type=row[2],
                file_size=row[3],
                status=DocumentStatus(row[4]),
                chunk_count=row[5],
                error_message=row[6],
                file_path=row[7]
            )
            for row in rows
        ]

    def delete_document(self, source_id: str) -> bool:
        """
        删除文档（物理删除）

        Args:
            source_id: 文档 source_id

        Returns:
            bool: 是否删除成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM documents
                WHERE source_id = ?
            """, (source_id,))

            conn.commit()
            affected_rows = cursor.rowcount

            if not self.is_memory_mode:
                conn.close()

            if affected_rows > 0:
                logger.info(f"删除文档: {source_id}")
                return True
            else:
                logger.warning(f"文档不存在: {source_id}")
                return False

        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False

    def save_chat(self, question: str, answer: str, sources: Optional[List[dict]] = None) -> bool:
        """
        保存问答记录到历史

        Args:
            question: 用户问题
            answer: AI 回答
            sources: 来源文档列表

        Returns:
            bool: 是否保存成功
        """
        try:
            import json

            conn = self._get_connection()
            cursor = conn.cursor()

            # 将 sources 转为 JSON 字符串
            sources_json = json.dumps(sources) if sources else None

            cursor.execute("""
                INSERT INTO chat_history (question, answer, sources)
                VALUES (?, ?, ?)
            """, (question, answer, sources_json))

            conn.commit()

            if not self.is_memory_mode:
                conn.close()

            logger.info(f"保存问答记录: {question[:50]}...")
            return True

        except Exception as e:
            logger.error(f"保存问答记录失败: {e}")
            return False

    def get_chat_history(self, limit: int = 50) -> List[dict]:
        """
        获取问答历史

        Args:
            limit: 返回记录数量限制

        Returns:
            List[dict]: 问答历史列表
        """
        try:
            import json

            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, question, answer, sources, timestamp
                FROM chat_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()

            if not self.is_memory_mode:
                conn.close()

            history = []
            for row in rows:
                # 解析 sources JSON
                sources = json.loads(row[3]) if row[3] else []

                history.append({
                    'id': row[0],
                    'question': row[1],
                    'answer': row[2],
                    'sources': sources,
                    'timestamp': row[4]
                })

            return history

        except Exception as e:
            logger.error(f"获取问答历史失败: {e}")
            return []

    def clear_chat_history(self) -> bool:
        """
        清空所有问答历史

        Returns:
            bool: 是否清空成功
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM chat_history")

            conn.commit()

            if not self.is_memory_mode:
                conn.close()

            logger.info("已清空问答历史")
            return True

        except Exception as e:
            logger.error(f"清空问答历史失败: {e}")
            return False
