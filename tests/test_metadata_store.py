"""
元数据存储单元测试

验证 SQLite 元数据存储的核心功能
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.storage.metadata_store import MetadataStore
from src.models.document import DocumentStatus
from src.utils.logger import setup_logger


def test_metadata_store():
    """测试元数据存储的完整功能"""

    # 初始化日志
    setup_logger(log_level="INFO")

    print("=" * 60)
    print("[TEST] 元数据存储测试")
    print("=" * 60)

    # 创建内存模式的存储（测试用）
    store = MetadataStore(":memory:")

    # 测试 1：创建文档
    print("\n[TEST 1] 创建文档")
    success = store.create_document(
        source_id="test123",
        file_name="test.pdf",
        file_type="pdf",
        file_size=1024 * 1024  # 1MB
    )
    assert success is True, "创建文档失败"
    print("[OK] 创建文档成功")

    # 测试 2：获取文档
    print("\n[TEST 2] 获取文档")
    doc = store.get_document("test123")
    assert doc is not None, "获取文档失败"
    assert doc.source_id == "test123"
    assert doc.file_name == "test.pdf"
    assert doc.status == DocumentStatus.INDEXING, "初始状态应该是 indexing"
    print(f"[OK] 获取文档成功: {doc.file_name}, 状态: {doc.status.value}")

    # 测试 3：更新状态为 active
    print("\n[TEST 3] 更新状态为 active")
    success = store.update_status(
        "test123",
        DocumentStatus.ACTIVE,
        chunk_count=10
    )
    assert success is True, "更新状态失败"

    doc = store.get_document("test123")
    assert doc.status == DocumentStatus.ACTIVE
    assert doc.chunk_count == 10
    print(f"[OK] 状态更新成功: {doc.status.value}, chunk_count={doc.chunk_count}")

    # 测试 4：更新状态为 failed
    print("\n[TEST 4] 更新状态为 failed")
    success = store.update_status(
        "test123",
        DocumentStatus.FAILED,
        error_message="PDF 解析失败"
    )
    assert success is True

    doc = store.get_document("test123")
    assert doc.status == DocumentStatus.FAILED
    assert doc.error_message == "PDF 解析失败"
    print(f"[OK] 状态更新成功: {doc.status.value}, error={doc.error_message}")

    # 测试 5：删除文档
    print("\n[TEST 5] 删除文档")
    success = store.delete_document("test123")
    assert success is True, "删除文档失败"

    doc = store.get_document("test123")
    assert doc is None, "文档应该已被删除"
    print("[OK] 文档删除成功")

    # 测试 6：列出文档
    print("\n[TEST 6] 创建多个文档并测试列表")
    store.create_document("doc1", "file1.pdf", "pdf", 100)
    store.create_document("doc2", "file2.md", "md", 200)

    docs = store.list_documents()
    assert len(docs) == 2, "应该有 2 个文档"
    print(f"[OK] 列出文档成功: 共 {len(docs)} 个")

    # 测试 7：按状态过滤
    print("\n[TEST 7] 按状态过滤")
    store.update_status("doc1", DocumentStatus.ACTIVE, chunk_count=5)
    store.update_status("doc2", DocumentStatus.INDEXING)

    active_docs = store.list_documents(DocumentStatus.ACTIVE)
    assert len(active_docs) == 1
    print(f"[OK] 状态过滤成功: ACTIVE 状态有 {len(active_docs)} 个文档")

    print("\n" + "=" * 60)
    print("[SUCCESS] 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    test_metadata_store()
