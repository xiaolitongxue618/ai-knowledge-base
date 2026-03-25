"""
诊断向量相似度问题
"""

import sys
import os
import tempfile
import shutil

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStoreManager
from src.llm.llm_client import OllamaClient
from src.processors.document_processor import DocumentProcessor
from src.processors.text_splitter import TextSplitter
from src.utils.logger import setup_logger


def diagnose_similarity():
    """诊断相似度计算"""

    setup_logger(log_level="INFO")

    print("=" * 70)
    print("[诊断] 向量相似度问题")
    print("=" * 70)

    # 初始化
    metadata_store = MetadataStore(":memory:")
    vector_store = VectorStoreManager(":memory:")
    llm_client = OllamaClient()
    processor = DocumentProcessor()
    splitter = TextSplitter(chunk_size=500, overlap=50)

    # 创建测试文档
    test_text = """# 人工智能基础

## 什么是人工智能？

人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
它致力于创造能够模仿人类智能的机器。

## 机器学习的类型

机器学习是人工智能的核心技术之一。

### 监督学习

监督学习使用标记的训练数据来学习输入和输出的映射关系。
"""

    # 创建临时文件
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "test.md")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(test_text)

    try:
        # 解析和分块
        text, metadata = processor.load_document(file_path)
        chunks = splitter.split(text, 'md')

        print(f"\n[信息] 文档分块: {len(chunks)} 个块")

        # 向量化
        print("\n[步骤 1] 向量化文档块...")
        embeddings = []
        for i, chunk in enumerate(chunks):
            emb = llm_client.embed(chunk['text'])
            embeddings.append(emb)
            print(f"  块 {i+1}: 向量维度 = {len(emb)}")

        # 存储到向量库
        chunk_ids = [f"test_chunk_{i}" for i in range(len(chunks))]
        chunk_metadatas = [
            {
                'chunk_id': f"chunk_{i}",
                'header': chunk['metadata'].get('header', ''),
            }
            for i, chunk in enumerate(chunks)
        ]

        vector_store.add_documents(
            texts=[c['text'] for c in chunks],
            embeddings=embeddings,
            metadatas=chunk_metadatas,
            ids=chunk_ids
        )

        print(f"\n[OK] 已存储 {len(chunk_ids)} 个向量")

        # 测试相似度检索
        print("\n[步骤 2] 测试相似度检索...")

        test_questions = [
            "什么是人工智能？",
            "机器学习有哪些类型？",
            "监督学习是什么？",
            "完全不相关的问题内容"
        ]

        for question in test_questions:
            print(f"\n问题: {question}")

            # 向量化问题
            question_embedding = llm_client.embed(question)

            # 检索
            results = vector_store.similarity_search(question_embedding, top_k=3)

            print(f"检索到 {len(results)} 个结果:")

            for i, result in enumerate(results, 1):
                distance = result.get('distance', 'N/A')
                similarity = result.get('similarity', 'N/A')
                header = result['metadata'].get('header', 'N/A')
                text_preview = result['text'][:50].replace('\n', ' ')

                print(f"  结果 {i}:")
                print(f"    距离: {distance}")
                print(f"    相似度: {similarity}")
                print(f"    标题: {header}")
                print(f"    预览: {text_preview}...")

            print("-" * 50)

        print("\n[分析]")
        print("如果距离值都很小（接近0），说明向量很相似")
        print("如果距离值都很大（>1.0），可能是距离度量配置问题")
        print("ChromaDB 默认使用 L2 距离，对于文本向量应该用余弦距离")

    finally:
        shutil.rmtree(temp_dir)
        print(f"\n[清理] 临时文件已删除")


if __name__ == "__main__":
    diagnose_similarity()
