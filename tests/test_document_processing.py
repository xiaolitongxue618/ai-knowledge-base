"""
文档解析测试

验证文档解析和分块功能
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.processors.document_processor import DocumentProcessor
from src.processors.text_splitter import TextSplitter
from src.utils.logger import setup_logger


def test_document_processing():
    """测试文档解析和分块"""

    # 初始化日志
    setup_logger(log_level="INFO")

    print("=" * 60)
    print("[TEST] 文档解析测试")
    print("=" * 60)

    # 1. 测试 Markdown 解析
    print("\n[TEST 1] Markdown 解析")
    processor = DocumentProcessor()
    splitter = TextSplitter(chunk_size=200, overlap=30)  # 小块用于测试

    test_file = "tests/fixtures/sample.md"
    if not os.path.exists(test_file):
        print(f"[ERROR] 测试文件不存在: {test_file}")
        return

    # 解析文档
    text, metadata = processor.load_document(test_file)
    print(f"[OK] 文档解析成功")
    print(f"   文件类型: {metadata['type']}")
    print(f"   文本长度: {len(text)} 字符")
    print(f"   标题结构: {len(metadata['structure'])} 个标题")

    # 2. 测试文本分块
    print("\n[TEST 2] 文本分块")
    chunks = splitter.split(text, file_type='md')

    print(f"[OK] 分块成功: 共 {len(chunks)} 个块")

    # 显示前 3 个块
    print("\n[INFO] 前 3 个块的内容：")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n--- 块 {i} ---")
        print(f"长度: {len(chunk['text'])} 字符")
        print(f"元数据: {chunk['metadata']}")
        preview = chunk['text'][:100]
        print(f"预览: {preview}...")

    # 3. 测试 MD5 计算
    print("\n[TEST 3] MD5 计算")
    md5_hash = processor.calculate_md5(test_file)
    print(f"[OK] MD5: {md5_hash}")

    # 4. 测试文件类型检测
    print("\n[TEST 4] 文件类型检测")
    types_to_test = [
        "test.pdf",
        "test.md",
        "test.txt",
        "test.docx"
    ]

    for filename in types_to_test:
        file_type = processor._detect_file_type(filename)
        print(f"   {filename} -> {file_type}")

    print("\n" + "=" * 60)
    print("[SUCCESS] 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_document_processing()
