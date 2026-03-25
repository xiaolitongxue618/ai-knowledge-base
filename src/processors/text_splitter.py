"""
文本分块模块
"""

from typing import List
import re

from src.utils.logger import logger


class TextSplitter:
    """文本分块器"""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        初始化文本分块器

        Args:
            chunk_size: 块大小（字符数）
            overlap: 重叠大小（字符数）
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

        logger.info(f"文本分块器初始化: chunk_size={chunk_size}, overlap={overlap}")

    def split(self, text: str, file_type: str = 'txt') -> List[dict]:
        """
        根据文件类型选择分块策略

        Args:
            text: 待分块文本
            file_type: 文件类型 (pdf/md/txt)

        Returns:
            List[dict]: 分块结果 [{'text': str, 'metadata': dict}, ...]
        """
        if file_type == 'md':
            return self._split_by_structure(text)
        else:
            return self._split_by_characters(text)

    def _split_by_structure(self, text: str) -> List[dict]:
        """
        Markdown 按结构分块（保留章节信息）

        Args:
            text: Markdown 文本

        Returns:
            List[dict]: 分块结果
        """
        chunks = []
        current_header = ""
        current_chunk = []

        lines = text.split('\n')

        for line in lines:
            # 检测标题
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                # 保存前一个块
                if current_chunk:
                    chunks.append({
                        'text': '\n'.join(current_chunk),
                        'metadata': {'header': current_header}
                    })
                    current_chunk = []

                current_header = header_match.group(2)
                current_chunk.append(line)
            else:
                current_chunk.append(line)

        # 最后一个块
        if current_chunk:
            chunks.append({
                'text': '\n'.join(current_chunk),
                'metadata': {'header': current_header}
            })

        # 二次切分过大的块
        chunks = self._split_large_chunks(chunks)

        logger.info(f"Markdown 结构分块完成: {len(chunks)} 个块")
        return chunks

    def _split_by_characters(self, text: str) -> List[dict]:
        """
        PDF/TXT 按字符数分块

        Args:
            text: 文本内容

        Returns:
            List[dict]: 分块结果

        Note:
            不保留页边界信息
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size

            # 尝试在段落边界切分
            if end < text_length:
                # 查找最近的段落结束（双换行）
                paragraph_end = text.rfind('\n\n', start, end)
                if paragraph_end > start + self.chunk_size // 2:
                    end = paragraph_end + 2
                else:
                    # 查找最近的句子结束（句号）
                    sentence_end = text.rfind('。', start, end)
                    if sentence_end > start + self.chunk_size // 2:
                        end = sentence_end + 1

            chunk_text = text[start:end].strip()

            if chunk_text:  # 忽略空块
                chunks.append({
                    'text': chunk_text,
                    'metadata': {'start': start, 'end': end}
                })

            start = end - self.overlap

        logger.info(f"字符数分块完成: {len(chunks)} 个块")
        return chunks

    def _split_large_chunks(self, chunks: List[dict]) -> List[dict]:
        """
        切分过大的块

        Args:
            chunks: 原始分块结果

        Returns:
            List[dict]: 切分后的结果
        """
        result = []
        for chunk in chunks:
            if len(chunk['text']) <= self.chunk_size * 1.5:
                result.append(chunk)
            else:
                # 递归切分
                sub_chunks = self._split_by_characters(chunk['text'])
                # 继承元数据
                for sub in sub_chunks:
                    sub['metadata'] = {**chunk['metadata'], **sub['metadata']}
                result.extend(sub_chunks)

        return result
