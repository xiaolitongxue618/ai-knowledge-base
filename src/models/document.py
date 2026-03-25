"""
文档数据模型
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class DocumentStatus(str, Enum):
    """文档状态枚举"""
    INDEXING = "indexing"  # 正在处理
    ACTIVE = "active"      # 可检索
    FAILED = "failed"      # 失败，可重试


@dataclass
class Document:
    """文档数据类"""
    source_id: str
    file_name: str
    file_type: str
    file_size: int
    status: DocumentStatus
    chunk_count: int = 0
    error_message: Optional[str] = None
    file_path: Optional[str] = None
