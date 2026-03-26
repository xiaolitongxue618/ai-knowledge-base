"""
RAG 链路模块
"""

from typing import Dict
import os

from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStoreManager
from src.llm.llm_client import OllamaClient
from src.processors.document_processor import DocumentProcessor
from src.processors.text_splitter import TextSplitter
from src.models.document import DocumentStatus
from src.utils.logger import logger


class RAGChain:
    """RAG 完整链路"""

    def __init__(
        self,
        vector_store: VectorStoreManager,
        llm_client: OllamaClient,
        metadata_store: MetadataStore,
        min_similarity: float = 0.5
    ):
        """
        初始化 RAG 链路

        Args:
            vector_store: 向量存储管理器
            llm_client: LLM 客户端
            metadata_store: 元数据存储
            min_similarity: 最小相似度阈值
        """
        self.vector_store = vector_store
        self.llm_client = llm_client
        self.metadata_store = metadata_store
        self.min_similarity = min_similarity

        # 初始化处理器
        self.document_processor = DocumentProcessor()
        self.text_splitter = TextSplitter(
            chunk_size=500,  # 可以从配置读取
            overlap=50
        )

        logger.info("RAG 链路初始化完成")

    def add_document(self, file_path: str) -> Dict:
        """
        添加文档（完整流程，含状态机）

        Args:
            file_path: 文件路径

        Returns:
            Dict: {success: bool, source_id: str, message: str}
        """
        source_id = None

        try:
            # 1. 计算来源 ID
            source_id = self.document_processor.calculate_md5(file_path)

            # 2. 检查是否已存在
            existing = self.metadata_store.get_document(source_id)
            if existing:
                if existing.status == DocumentStatus.ACTIVE:
                    return {
                        'success': False,
                        'message': f'文档已存在且处于活跃状态: {existing.file_name}'
                    }
                elif existing.status == DocumentStatus.INDEXING:
                    return {
                        'success': False,
                        'message': '文档正在处理中，请稍后'
                    }
                elif existing.status == DocumentStatus.FAILED:
                    # 允许重试：更新状态为 indexing
                    self.metadata_store.update_status(
                        source_id,
                        DocumentStatus.INDEXING
                    )
                    logger.info(f'重试失败文档: {source_id}')

            # 3. 创建新记录（状态为 indexing）
            if not existing:
                file_name = os.path.basename(file_path)
                file_type = self.document_processor._detect_file_type(file_path)
                file_size = os.path.getsize(file_path)

                success = self.metadata_store.create_document(
                    source_id=source_id,
                    file_name=file_name,
                    file_type=file_type,
                    file_size=file_size,
                    file_path=file_path
                )

                if not success:
                    return {
                        'success': False,
                        'message': '创建文档记录失败（可能 source_id 冲突）'
                    }

            # 4. 解析文档
            logger.info(f"开始解析文档: {file_path}")
            text, metadata = self.document_processor.load_document(file_path)

            # 5. 分块
            logger.info("开始文本分块...")
            chunks = self.text_splitter.split(text, metadata['type'])
            logger.info(f"文档分块完成: {len(chunks)} 个块")

            # 6. 向量化
            logger.info("开始向量化...")
            embeddings = []
            for i, chunk in enumerate(chunks):
                emb = self.llm_client.embed(chunk['text'])
                embeddings.append(emb)
                if (i + 1) % 10 == 0:
                    logger.info(f"向量化进度: {i + 1}/{len(chunks)}")

            # 7. 存储到向量库
            chunk_ids = [f"{source_id}_chunk_{i}" for i in range(len(chunks))]
            chunk_metadatas = [
                {
                    'source_id': source_id,
                    'source_name': os.path.basename(file_path),
                    'chunk_id': f"chunk_{i}",
                    'file_type': metadata['type'],
                    **chunk['metadata']
                }
                for i, chunk in enumerate(chunks)
            ]

            self.vector_store.add_documents(
                texts=[c['text'] for c in chunks],
                embeddings=embeddings,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )

            # 8. 更新状态为 active
            self.metadata_store.update_status(
                source_id,
                DocumentStatus.ACTIVE,
                chunk_count=len(chunks)
            )

            logger.info(f"文档处理成功: {source_id}, {len(chunks)} 个块")

            return {
                'success': True,
                'source_id': source_id,
                'message': f'成功处理文档，共 {len(chunks)} 个块'
            }

        except Exception as e:
            # 失败时更新状态为 failed
            if source_id:
                self.metadata_store.update_status(
                    source_id,
                    DocumentStatus.FAILED,
                    error_message=str(e)
                )

            logger.error(f"文档处理失败: {source_id}, 错误: {e}")
            return {
                'success': False,
                'message': f'处理失败: {str(e)}'
            }

    def delete_document(self, source_id: str) -> Dict:
        """
        删除文档（物理删除）

        Args:
            source_id: 文档 source_id

        Returns:
            Dict: {success: bool, message: str}
        """
        try:
            # 1. 从向量库删除
            self.vector_store.delete_by_source(source_id)

            # 2. 从元数据删除（物理删除）
            success = self.metadata_store.delete_document(source_id)

            if success:
                logger.info(f"文档删除成功: {source_id}")
                return {
                    'success': True,
                    'message': '文档已删除'
                }
            else:
                return {
                    'success': False,
                    'message': '文档不存在'
                }

        except Exception as e:
            logger.error(f"文档删除失败: {source_id}, 错误: {e}")
            return {
                'success': False,
                'message': f'删除失败: {str(e)}'
            }

    def ask(
        self,
        question: str,
        top_k: int = 3,
        temperature: float = 0.7
    ) -> Dict:
        """
        提问（完整 RAG 流程）

        Args:
            question: 用户问题
            top_k: 检索的文档块数量
            temperature: LLM 温度参数

        Returns:
            Dict: {
                'answer': str,  # 答案
                'sources': List[Dict],  # 检索到的来源
                'question': str  # 原始问题
            }
        """
        try:
            logger.info(f"收到问题: {question}")

            # 1. 问题向量化
            question_embedding = self.llm_client.embed(question)

            # 2. 检索相关文档块
            results = self.vector_store.similarity_search(
                question_embedding,
                top_k=top_k
            )

            # 过滤低相似度结果
            filtered_results = [
                r for r in results
                if r['similarity'] >= self.min_similarity
            ]

            if not filtered_results:
                logger.warning(f"未找到相关文档，相似度阈值: {self.min_similarity}")
                return {
                    'answer': '抱歉，我在知识库中没有找到相关信息来回答您的问题。',
                    'sources': [],
                    'question': question
                }

            logger.info(f"检索到 {len(filtered_results)} 个相关文档块")

            # 3. 构建上下文
            context_parts = []
            for i, result in enumerate(filtered_results, 1):
                source_name = result['metadata'].get('source_name', '未知来源')
                header = result['metadata'].get('header', '')
                text = result['text']
                similarity = result['similarity']

                context_parts.append(
                    f"[来源 {i}] {source_name}"
                    + (f" ({header})" if header else "")
                    + f"\n{text}\n"
                )

            context = "\n".join(context_parts)

            # 4. 构建提示词
            prompt = f"""你是一个温暖、贴心的AI学习伙伴。请根据以下参考信息回答用户的问题，让你的回答充满人情味。

【参考信息】
{context}

【用户问题】
{question}

【回答风格要求】
🌟 **语气温暖**：像朋友一样交流，使用"我为你找到了...""希望这对你有帮助"这样的表达
💝 **表达同理心**：理解用户的学习需求，给出鼓励和支持
✨ **自然对话**：避免机械化和过度格式化，像真人聊天一样自然
🎯 **准确可靠**：只使用参考信息中的内容，不要编造

【内容要求】
1. 如果参考信息足以回答：用温暖、清晰的语气解释，可以适当举例说明
2. 如果信息不足以完整回答：坦诚地说"抱歉，我手头的资料里没有完整的答案，不过..."
3. 如果完全不相关：温暖地说明"这个话题超出了我目前知识库的范围，但我建议你可以..."

【特别提醒】
- 让每一句话都体现出你想帮助用户的诚意
- 可以适当使用鼓励的话语，如"这是个很好的问题！""你在学习的路上并不孤单"
- 避免冰冷的"根据文档1、文档2"这种机械表述
- 用"我注意到...""我理解你..."这样的表达拉近距离

请用温暖贴心的语气回答："""

            # 5. LLM 生成答案
            logger.info("调用 LLM 生成答案...")
            answer = self.llm_client.generate(prompt, temperature=temperature)

            # 6. 整理来源信息
            sources = [
                {
                    'source_name': r['metadata'].get('source_name', '未知来源'),
                    'header': r['metadata'].get('header', ''),
                    'text': r['text'][:200] + '...' if len(r['text']) > 200 else r['text'],
                    'similarity': r['similarity']
                }
                for r in filtered_results
            ]

            logger.info(f"问题回答成功，答案长度: {len(answer)}")

            return {
                'answer': answer,
                'sources': sources,
                'question': question
            }

        except Exception as e:
            logger.error(f"回答问题失败: {e}")
            return {
                'answer': f'抱歉，处理您的问题时出错：{str(e)}',
                'sources': [],
                'question': question
            }
