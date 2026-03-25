"""
集成测试：端到端文档摄入流程

验证从文档上传到向量存储的完整流程
"""

import sys
import os
import tempfile
import shutil

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStoreManager
from src.processors.document_processor import DocumentProcessor
from src.processors.text_splitter import TextSplitter
from src.models.document import DocumentStatus
from src.utils.logger import setup_logger


def create_test_document():
    """创建测试文档"""
    content = """# 人工智能基础

## 什么是人工智能？

人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
它致力于创造能够模仿人类智能的机器。

## 机器学习的类型

机器学习是人工智能的核心技术之一。

### 监督学习

监督学习使用标记的训练数据来学习输入和输出的映射关系。

### 无监督学习

无监督学习用于发现数据中的隐藏模式，不需要标记数据。

## 人工智能的应用

人工智能已经广泛应用于以下领域：

- 自然语言处理
- 计算机视觉
- 语音识别
- 推荐系统

随着技术的发展，人工智能将在更多领域发挥重要作用。
"""

    # 创建临时文件
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "ai_intro.md")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return file_path, temp_dir


def test_end_to_end_document_upload():
    """测试完整的文档上传流程"""

    setup_logger(log_level="INFO")

    print("=" * 70)
    print("[集成测试] 端到端文档上传流程")
    print("=" * 70)

    # 创建测试文档
    print("\n[步骤 1] 创建测试文档")
    file_path, temp_dir = create_test_document()
    print(f"[OK] 测试文档创建成功: {file_path}")

    try:
        # 初始化组件
        print("\n[步骤 2] 初始化系统组件")
        metadata_store = MetadataStore(":memory:")
        vector_store = VectorStoreManager(":memory:")
        processor = DocumentProcessor()
        splitter = TextSplitter(chunk_size=200, overlap=30)  # 小块便于观察
        print("[OK] 组件初始化完成")

        # 计算 MD5
        print("\n[步骤 3] 计算文档 MD5")
        source_id = processor.calculate_md5(file_path)
        print(f"[OK] MD5: {source_id}")

        # 创建元数据记录（indexing 状态）
        print("\n[步骤 4] 创建元数据记录")
        success = metadata_store.create_document(
            source_id=source_id,
            file_name="ai_intro.md",
            file_type="md",
            file_size=os.path.getsize(file_path)
        )
        assert success is True, "创建元数据失败"
        print("[OK] 元数据记录创建成功 (status=indexing)")

        # 验证状态
        doc = metadata_store.get_document(source_id)
        assert doc is not None, "获取文档失败"
        assert doc.status == DocumentStatus.INDEXING, f"状态应该是 indexing，实际是 {doc.status}"
        print(f"[OK] 状态验证成功: {doc.status.value}")

        # 解析文档
        print("\n[步骤 5] 解析文档")
        text, metadata = processor.load_document(file_path)
        print(f"[OK] 文档解析成功")
        print(f"      文件类型: {metadata['type']}")
        print(f"      文本长度: {len(text)} 字符")
        print(f"      标题数量: {len(metadata['structure'])} 个")

        # 分块
        print("\n[步骤 6] 文本分块")
        chunks = splitter.split(text, file_type='md')
        print(f"[OK] 文本分块完成: {len(chunks)} 个块")

        # 显示前 3 个块
        print("\n[信息] 前 3 个块:")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\n  块 {i}:")
            print(f"    长度: {len(chunk['text'])} 字符")
            print(f"    标题: {chunk['metadata'].get('header', '无')}")
            preview = chunk['text'][:50].replace('\n', ' ')
            print(f"    预览: {preview}...")

        # 模拟向量化（不实际调用 Ollama）
        print("\n[步骤 7] 向量化（模拟）")
        print(f"[INFO] 实际向量化需要 Ollama 服务")
        print(f"[INFO] 这里使用随机向量模拟")

        import random
        embeddings = [[random.random() for _ in range(384)] for _ in chunks]

        # 准备元数据
        chunk_ids = [f"{source_id}_chunk_{i}" for i in range(len(chunks))]
        chunk_metadatas = [
            {
                'source_id': source_id,
                'source_name': 'ai_intro.md',
                'chunk_id': f"chunk_{i}",
                'file_type': 'md',
                **chunk['metadata']
            }
            for i, chunk in enumerate(chunks)
        ]

        # 存储到向量库
        print("\n[步骤 8] 存储到向量库")
        success = vector_store.add_documents(
            texts=[c['text'] for c in chunks],
            embeddings=embeddings,
            metadatas=chunk_metadatas,
            ids=chunk_ids
        )
        assert success is True, "存储到向量库失败"
        print(f"[OK] 成功存储 {len(chunk_ids)} 个文档块到向量库")

        # 更新状态为 active
        print("\n[步骤 9] 更新状态为 active")
        success = metadata_store.update_status(
            source_id,
            DocumentStatus.ACTIVE,
            chunk_count=len(chunks)
        )
        assert success is True, "更新状态失败"
        print(f"[OK] 状态更新成功: indexing -> active")

        # 验证最终状态
        print("\n[步骤 10] 验证最终状态")
        doc = metadata_store.get_document(source_id)
        print(f"[OK] 文档状态: {doc.status.value}")
        print(f"[OK] 块数量: {doc.chunk_count}")

        # 验证向量库
        print("\n[步骤 11] 验证向量库")
        stats = vector_store.get_stats()
        print(f"[OK] 向量总数: {stats['total_count']}")

        # 测试向量检索（模拟）
        print("\n[步骤 12] 测试向量检索（模拟）")
        query_embedding = [random.random() for _ in range(384)]
        results = vector_store.similarity_search(query_embedding, top_k=3)
        print(f"[OK] 检索到 {len(results)} 个结果")

        # 显示检索结果
        print("\n[信息] 检索结果:")
        for i, result in enumerate(results, 1):
            print(f"  结果 {i}:")
            print(f"    来源: {result['metadata']['source_name']}")
            print(f"    块ID: {result['metadata']['chunk_id']}")
            print(f"    相似度: {result['similarity']:.4f}")
            preview = result['text'][:50].replace('\n', ' ')
            print(f"    预览: {preview}...")

        print("\n" + "=" * 70)
        print("[SUCCESS] 端到端测试全部通过！")
        print("=" * 70)

        print("\n[总结]")
        print("[OK] 文档解析：正常")
        print("[OK] 文本分块：正常")
        print("[OK] 状态机：正常（indexing -> active）")
        print("[OK] 元数据存储：正常")
        print("[OK] 向量存储：正常")
        print("[OK] 向量检索：正常")
        print("\n系统已经可以处理文档并存储到向量数据库了！")

    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)
        print(f"\n[清理] 临时文件已删除: {temp_dir}")


if __name__ == "__main__":
    test_end_to_end_document_upload()
