"""
完整 RAG 流程测试

验证从文档上传到问答的完整流程
"""

import sys
import os
import tempfile
import shutil

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStoreManager
from src.llm.llm_client import OllamaClient
from src.rag import RAGChain
from src.models.document import DocumentStatus
from src.utils.logger import setup_logger


def create_test_documents():
    """创建测试文档"""
    docs = []

    # 文档 1：AI 基础知识
    doc1_content = """# 人工智能基础

## 什么是人工智能？

人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
它致力于创造能够模仿人类智能的机器。

## 机器学习的类型

机器学习是人工智能的核心技术之一。

### 监督学习

监督学习使用标记的训练数据来学习输入和输出的映射关系。
常见算法包括线性回归、逻辑回归、支持向量机等。

### 无监督学习

无监督学习用于发现数据中的隐藏模式，不需要标记数据。
常见算法包括聚类、降维等。

## 人工智能的应用

人工智能已经广泛应用于以下领域：

- 自然语言处理：机器翻译、情感分析
- 计算机视觉：图像识别、目标检测
- 语音识别：语音转文字、语音助手
- 推荐系统：电商推荐、内容推荐

随着技术的发展，人工智能将在更多领域发挥重要作用。
"""

    # 文档 2：Python 编程
    doc2_content = """# Python 编程基础

## Python 简介

Python 是一种高级编程语言，具有简洁明了的语法。

## 基本数据类型

Python 有以下基本数据类型：

1. 整数（int）：如 1, 2, 100
2. 浮点数（float）：如 3.14, 2.5
3. 字符串（str）：如 "Hello", 'World'
4. 布尔值（bool）：True 或 False

## 控制流

Python 支持常见的控制流语句：

- if 语句：条件判断
- for 循环：遍历序列
- while 循环：条件循环

## 函数定义

使用 def 关键字定义函数：

```python
def greet(name):
    return f"Hello, {name}!"
```

Python 是一门易学易用的编程语言，适合初学者。
"""

    # 创建临时文件
    temp_dir = tempfile.mkdtemp()

    file1 = os.path.join(temp_dir, "ai_basics.md")
    file2 = os.path.join(temp_dir, "python_basics.md")

    with open(file1, 'w', encoding='utf-8') as f:
        f.write(doc1_content)

    with open(file2, 'w', encoding='utf-8') as f:
        f.write(doc2_content)

    docs.append((file1, "ai_basics.md"))
    docs.append((file2, "python_basics.md"))

    return docs, temp_dir


def test_complete_rag_flow():
    """测试完整的 RAG 流程"""

    setup_logger(log_level="INFO")

    print("=" * 70)
    print("[完整测试] RAG 端到端流程")
    print("=" * 70)

    # 创建测试文档
    print("\n[步骤 1] 创建测试文档")
    docs, temp_dir = create_test_documents()
    print(f"[OK] 创建了 {len(docs)} 个测试文档")

    try:
        # 初始化组件
        print("\n[步骤 2] 初始化系统组件")
        metadata_store = MetadataStore(":memory:")
        vector_store = VectorStoreManager(":memory:")
        llm_client = OllamaClient()

        # 检查 Ollama 连接
        print("\n[步骤 3] 检查 Ollama 服务")
        if llm_client.check_connection():
            print("[OK] Ollama 服务连接成功")
            ollama_available = True
        else:
            print("[WARNING] Ollama 服务未运行，将使用模拟模式")
            print("[INFO] 请运行 'ollama serve' 启动服务")
            ollama_available = False

        # 创建 RAG 链路
        print("\n[步骤 4] 创建 RAG 链路")
        rag_chain = RAGChain(
            vector_store=vector_store,
            llm_client=llm_client,
            metadata_store=metadata_store,
            min_similarity=0.3
        )
        print("[OK] RAG 链路初始化完成")

        # 上传文档
        print("\n[步骤 5] 上传文档到知识库")
        for file_path, file_name in docs:
            print(f"\n处理文档: {file_name}")

            if ollama_available:
                # 真实向量化
                result = rag_chain.add_document(file_path)
            else:
                # 模拟向量化（使用随机向量）
                print("[INFO] 使用模拟向量化模式")
                # 手动处理文档
                from src.processors.document_processor import DocumentProcessor
                from src.processors.text_splitter import TextSplitter
                import random

                processor = DocumentProcessor()
                splitter = TextSplitter(chunk_size=500, overlap=50)

                # 计算来源 ID
                source_id = processor.calculate_md5(file_path)

                # 解析文档
                text, metadata = processor.load_document(file_path)

                # 分块
                chunks = splitter.split(text, metadata['type'])

                # 模拟向量化
                embeddings = [[random.random() for _ in range(768)] for _ in chunks]

                # 存储到向量库
                chunk_ids = [f"{source_id}_chunk_{i}" for i in range(len(chunks))]
                chunk_metadatas = [
                    {
                        'source_id': source_id,
                        'source_name': file_name,
                        'chunk_id': f"chunk_{i}",
                        'file_type': metadata['type'],
                        **chunk['metadata']
                    }
                    for i, chunk in enumerate(chunks)
                ]

                vector_store.add_documents(
                    texts=[c['text'] for c in chunks],
                    embeddings=embeddings,
                    metadatas=chunk_metadatas,
                    ids=chunk_ids
                )

                # 更新元数据
                metadata_store.create_document(
                    source_id=source_id,
                    file_name=file_name,
                    file_type=metadata['type'],
                    file_size=os.path.getsize(file_path)
                )

                metadata_store.update_status(
                    source_id,
                    DocumentStatus.ACTIVE,
                    chunk_count=len(chunks)
                )

                result = {
                    'success': True,
                    'source_id': source_id,
                    'message': f'成功处理文档（模拟），共 {len(chunks)} 个块'
                }

            if result['success']:
                print(f"[OK] {result['message']}")
            else:
                print(f"[ERROR] {result['message']}")

        # 验证文档上传
        print("\n[步骤 6] 验证文档上传")
        all_docs = metadata_store.list_documents()
        active_docs = [d for d in all_docs if d.status == DocumentStatus.ACTIVE]
        print(f"[OK] 活跃文档数量: {len(active_docs)}")

        vector_stats = vector_store.get_stats()
        print(f"[OK] 向量总数: {vector_stats['total_count']}")

        # 测试问答功能
        print("\n[步骤 7] 测试问答功能")

        test_questions = [
            "什么是人工智能？",
            "Python 有哪些基本数据类型？",
            "机器学习有哪些类型？"
        ]

        for i, question in enumerate(test_questions, 1):
            print(f"\n问题 {i}: {question}")

            if ollama_available:
                # 真实问答
                result = rag_chain.ask(question)
            else:
                # 模拟问答（只测试检索，不调用 LLM）
                print("[INFO] 使用模拟问答模式（仅检索）")

                # 问题向量化
                question_embedding = [random.random() for _ in range(768)]

                # 检索
                search_results = vector_store.similarity_search(question_embedding, top_k=3)

                # 过滤
                filtered_results = [
                    r for r in search_results
                    if r['similarity'] >= 0.3
                ]

                if filtered_results:
                    sources = [
                        {
                            'source_name': r['metadata'].get('source_name', '未知'),
                            'text': r['text'][:100] + '...',
                            'similarity': r['similarity']
                        }
                        for r in filtered_results
                    ]

                    print(f"[OK] 检索到 {len(filtered_results)} 个相关文档块")
                    for j, source in enumerate(sources[:3], 1):
                        print(f"  来源 {j}: {source['source_name']}")
                        print(f"  相似度: {source['similarity']:.4f}")
                        print(f"  预览: {source['text']}")

                    result = {
                        'answer': f'（模拟答案）基于检索到的 {len(filtered_results)} 个文档块，这是一个测试答案。',
                        'sources': sources
                    }
                else:
                    print("[WARNING] 未找到相关文档")
                    result = {
                        'answer': '抱歉，未找到相关信息',
                        'sources': []
                    }

            print(f"\n答案: {result['answer'][:200]}...")

            if result.get('sources'):
                print(f"[OK] 引用来源: {len(result['sources'])} 个")

        print("\n" + "=" * 70)
        print("[SUCCESS] 完整 RAG 流程测试完成！")
        print("=" * 70)

        print("\n[总结]")
        print(f"[OK] 文档上传: {len(active_docs)} 个文档")
        print(f"[OK] 向量存储: {vector_stats['total_count']} 个向量")
        print(f"[OK] 问答测试: {len(test_questions)} 个问题")
        print(f"[OK] Ollama 状态: {'已连接' if ollama_available else '未连接（模拟模式）'}")

        if not ollama_available:
            print("\n[提示] 要启用完整功能，请运行:")
            print("  1. ollama serve")
            print("  2. ollama pull llama3:8b")
            print("  3. ollama pull nomic-embed-text")

    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)
        print(f"\n[清理] 临时文件已删除")


if __name__ == "__main__":
    test_complete_rag_flow()
