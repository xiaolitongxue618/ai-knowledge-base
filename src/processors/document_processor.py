"""
文档处理模块
"""

from typing import Tuple, Dict
from pathlib import Path
import hashlib

from src.utils.logger import logger


class DocumentProcessor:
    """文档处理核心类"""

    def __init__(self):
        """初始化文档处理器"""
        pass

    def load_document(self, file_path: str) -> Tuple[str, Dict]:
        """
        加载文档并提取文本

        Args:
            file_path: 文件路径

        Returns:
            (text, metadata): 文本内容和元数据

        Raises:
            ValueError: 不支持的文件类型
        """
        file_type = self._detect_file_type(file_path)

        if file_type == 'pdf':
            return self._parse_pdf(file_path)
        elif file_type == 'md':
            return self._parse_markdown(file_path)
        elif file_type == 'txt':
            return self._parse_text(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")

    def _parse_pdf(self, file_path: str) -> Tuple[str, Dict]:
        """
        解析 PDF 文件

        Args:
            file_path: PDF 文件路径

        Returns:
            (text, metadata): 文本内容和元数据

        Note:
            v1.0 不保证页码级定位精度
        """
        import pypdf

        try:
            reader = pypdf.PdfReader(file_path)
            text_parts = []

            # 提取每页文本
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"PDF 第 {page_num + 1} 页解析失败: {e}")

            # 合并所有页
            full_text = "\n\n".join(text_parts)

            metadata = {
                'type': 'pdf',
                'pages': len(reader.pages),
                'title': reader.metadata.get('/Title', '') if reader.metadata else ''
            }

            logger.info(f"PDF 解析成功: {file_path} ({len(text_parts)} 页)")
            return full_text, metadata

        except Exception as e:
            logger.error(f"PDF 解析失败: {file_path}, 错误: {e}")
            raise

    def _parse_markdown(self, file_path: str) -> Tuple[str, Dict]:
        """
        解析 Markdown 文件

        Args:
            file_path: Markdown 文件路径

        Returns:
            (text, metadata): 文本内容和元数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取标题结构
            metadata = {
                'type': 'md',
                'structure': self._extract_md_structure(content)
            }

            logger.info(f"Markdown 解析成功: {file_path}")
            return content, metadata

        except Exception as e:
            logger.error(f"Markdown 解析失败: {file_path}, 错误: {e}")
            raise

    def _parse_text(self, file_path: str) -> Tuple[str, Dict]:
        """
        解析纯文本文件

        Args:
            file_path: 文本文件路径

        Returns:
            (text, metadata): 文本内容和元数据
        """
        try:
            # 尝试 UTF-8 编码
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            metadata = {'type': 'txt'}

            logger.info(f"文本文件解析成功: {file_path}")
            return text, metadata

        except UnicodeDecodeError:
            # 尝试 GBK 编码（中文环境常见）
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    text = f.read()

                metadata = {'type': 'txt', 'encoding': 'gbk'}
                logger.info(f"文本文件解析成功 (GBK): {file_path}")
                return text, metadata

            except Exception as e:
                logger.error(f"文本文件解析失败 (尝试了 UTF-8 和 GBK): {file_path}, 错误: {e}")
                raise

    def calculate_md5(self, file_path: str) -> str:
        """
        计算文件 MD5 哈希（作为 source_id）

        Args:
            file_path: 文件路径

        Returns:
            str: MD5 哈希值
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        md5_value = hash_md5.hexdigest()
        logger.debug(f"计算 MD5: {file_path} -> {md5_value}")

        return md5_value

    def _detect_file_type(self, file_path: str) -> str:
        """
        检测文件类型

        Args:
            file_path: 文件路径

        Returns:
            str: 文件类型 (pdf/md/txt/unknown)
        """
        suffix = Path(file_path).suffix.lower()
        type_map = {'.pdf': 'pdf', '.md': 'md', '.txt': 'txt'}
        return type_map.get(suffix, 'unknown')

    def _extract_md_structure(self, content: str) -> list:
        """
        提取 Markdown 标题结构

        Args:
            content: Markdown 内容

        Returns:
            list: 标题列表 [{'level': int, 'title': str}, ...]
        """
        import re
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        return [{'level': len(h), 'title': title.strip()} for h, title in headers]
