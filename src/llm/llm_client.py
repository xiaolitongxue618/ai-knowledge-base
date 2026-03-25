"""
Ollama LLM 客户端
"""

from typing import List
import ollama

from src.config import settings
from src.utils.logger import logger


class OllamaClient:
    """Ollama LLM 客户端"""

    def __init__(
        self,
        model: str = None,
        embedding_model: str = None,
        base_url: str = None
    ):
        """
        初始化 Ollama 客户端

        Args:
            model: LLM 模型名称
            embedding_model: Embedding 模型名称
            base_url: Ollama 服务地址
        """
        self.model = model or settings.ollama_model
        self.embedding_model = embedding_model or settings.embedding_model
        self.base_url = base_url or settings.ollama_base_url

        self.client = ollama.Client(host=self.base_url)

        logger.info(f"Ollama 客户端初始化: model={self.model}, embedding={self.embedding_model}")

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        生成答案

        Args:
            prompt: 提示词
            temperature: 温度参数 (0-1)

        Returns:
            str: 生成的文本
        """
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={'temperature': temperature}
            )

            logger.debug(f"LLM 生成成功，输出长度: {len(response['response'])}")
            return response['response']

        except Exception as e:
            logger.error(f"LLM 生成失败: {e}")
            raise

    def embed(self, text: str) -> List[float]:
        """
        生成文本向量

        Args:
            text: 输入文本

        Returns:
            List[float]: 向量表示
        """
        try:
            response = self.client.embeddings(
                model=self.embedding_model,
                prompt=text
            )

            embedding = response['embedding']
            logger.debug(f"文本向量化成功: 维度={len(embedding)}")

            return embedding

        except Exception as e:
            logger.error(f"向量化失败: {e}")
            raise

    def check_connection(self) -> bool:
        """
        检查 Ollama 服务是否可用

        Returns:
            bool: 是否可用
        """
        try:
            self.client.list()
            logger.info("Ollama 服务连接正常")
            return True
        except Exception as e:
            logger.error(f"Ollama 服务连接失败: {e}")
            return False
