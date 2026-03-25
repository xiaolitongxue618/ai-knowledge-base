"""
向量存储模块（ChromaDB）
"""

import chromadb
from typing import List, Dict, Optional

from src.utils.logger import logger


class VectorStoreManager:
    """ChromaDB 向量存储管理器"""

    def __init__(self, persist_directory: str = "./data/vector_store"):
        """
        初始化向量存储

        Args:
            persist_directory: 持久化目录路径，":memory:" 表示内存模式（测试用）
        """
        if persist_directory == ":memory:":
            # 测试模式：临时内存客户端
            self.client = chromadb.Client()
            logger.info("向量存储初始化: 内存模式（测试）")
        else:
            # 生产模式：持久化
            from pathlib import Path
            Path(persist_directory).mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(path=persist_directory)
            logger.info(f"向量存储初始化: {persist_directory}")

        # 获取或创建集合（使用余弦距离，适合文本向量）
        try:
            # 尝试获取现有集合
            self.collection = self.client.get_collection(name="knowledge_base")
            # 如果集合存在但没有使用余弦距离，需要删除重建
            if self.collection.metadata.get("hnsw:space") != "cosine":
                logger.warning("检测到旧集合使用非余弦距离，删除重建...")
                self.client.delete_collection(name="knowledge_base")
                raise ValueError("需要重建集合")
        except:
            # 创建新集合，使用余弦距离
            self.collection = self.client.create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine", "version": "1.0"}
            )
            logger.info("创建新向量集合: 使用余弦距离")

        logger.info(f"向量集合已加载: {self.collection.name} (总数: {self.collection.count()})")

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
        ids: List[str]
    ) -> bool:
        """
        添加文档到向量库

        Args:
            texts: 文本块列表
            embeddings: 向量列表
            metadatas: 元数据列表
            ids: 文档 ID 列表

        Returns:
            bool: 是否成功
        """
        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"成功添加 {len(ids)} 个文档块到向量库")
            return True

        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 3
    ) -> List[dict]:
        """
        相似度检索

        Args:
            query_embedding: 查询向量
            top_k: 返回 top-k 结果

        Returns:
            List[dict]: 检索结果列表
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            # 格式化结果
            formatted = []
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i] if 'distances' in results else None
                # 余弦距离转相似度：距离 0-2 → 相似度 1-0
                similarity = 1 - (distance / 2) if distance is not None else None

                formatted.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': distance,
                    'similarity': similarity
                })

            return formatted

        except Exception as e:
            logger.error(f"相似度检索失败: {e}")
            return []

    def delete_by_source(self, source_id: str) -> bool:
        """
        删除指定 source_id 的所有向量

        Args:
            source_id: 文档 source_id

        Returns:
            bool: 是否成功
        """
        try:
            self.collection.delete(
                where={"source_id": source_id}
            )

            logger.info(f"删除向量: {source_id}")
            return True

        except Exception as e:
            logger.error(f"删除向量失败: {e}")
            return False

    def get_stats(self) -> dict:
        """
        获取向量库统计信息

        Returns:
            dict: 统计信息
        """
        return {
            'total_count': self.collection.count(),
            'collection_name': self.collection.name
        }
