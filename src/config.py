"""
配置管理模块
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # Ollama 配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:0.5b"
    embedding_model: str = "nomic-embed-text"

    # 应用配置
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 3
    min_similarity: float = 0.5  # 余弦距离下，0.5 相当于距离 1.0（中等相关）

    # 路径配置
    data_dir: str = "./data"
    vector_store_dir: str = "./data/vector_store"
    metadata_db: str = "./data/metadata/knowledge_base.db"
    log_file: str = "./logs/app.log"

    # 日志配置
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
