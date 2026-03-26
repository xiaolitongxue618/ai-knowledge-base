"""检查云端知识库文档质量"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.config import settings
from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStoreManager

def main():
    print("=" * 80)
    print("知识库文档深度诊断")
    print("=" * 80)
    print()

    # 初始化
    metadata_store = MetadataStore(settings.metadata_db)
    vector_store = VectorStoreManager(settings.vector_store_dir)

    # 获取所有文档
    docs = metadata_store.list_documents()

    print(f"总文档数: {len(docs)}")
    print()

    if len(docs) == 0:
        print("[WARNING] 知识库为空！")
        return

    # 分类统计
    technical_docs = []      # 技术文档
    conversation_docs = []   # 对话记录
    invalid_docs = []        # 无效文档

    for i, doc in enumerate(docs, 1):
        print(f"[{i}/{len(docs)}] 检查: {doc.file_name}")
        print(f"    路径: {doc.file_path}")
        print(f"    存在: {os.path.exists(doc.file_path)}")

        if not os.path.exists(doc.file_path):
            invalid_docs.append(doc)
            print(f"    [INVALID] 文件不存在")
            print()
            continue

        # 读取内容
        try:
            with open(doc.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"    大小: {len(content)} 字符")

            # 检查内容特征
            lines = content.split('\n')
            non_empty_lines = [l.strip() for l in lines if l.strip()]

            # 特征检测
            has_code_markers = any(marker in content for marker in ['```', 'def ', 'class ', 'import ', 'function '])
            has_conversation_pattern = any(pattern in content for pattern in ['你好', '很高兴', '请问', '我想用', '帮我'])
            has_technical_terms = any(term in content for term in ['API', 'pip install', 'LangChain', 'RAG', 'Agent', 'Embedding', '向量', '模型'])

            # 判断文档类型
            if has_conversation_pattern and not has_technical_terms and not has_code_markers:
                # 对话记录
                conversation_ratio = len([l for l in non_empty_lines if any(p in l for p in ['你好', '请问', '谢谢', '再见'])]) / max(len(non_empty_lines), 1)

                if conversation_ratio > 0.1:
                    doc_type = "对话记录"
                    conversation_docs.append(doc)
                    print(f"    [CONVERSATION] 疑似对话记录（对话占比 {conversation_ratio*100:.1f}%）")
                else:
                    doc_type = "未知"
            elif has_technical_terms or has_code_markers:
                doc_type = "技术文档"
                technical_docs.append(doc)
                print(f"    [TECHNICAL] 技术文档")
            else:
                doc_type = "其他"
                print(f"    [OTHER] 类型未知")

            # 显示内容预览
            preview_lines = content.split('\n')[:5]
            print(f"    内容预览:")
            for line in preview_lines:
                if line.strip():
                    print(f"      {line.strip()[:80]}")

            print(f"    诊断: {doc_type}")
            print()

        except Exception as e:
            print(f"    [ERROR] 读取失败: {e}")
            print()

    # 统计报告
    print("=" * 80)
    print("诊断报告")
    print("=" * 80)
    print(f"技术文档: {len(technical_docs)} 个")
    print(f"对话记录: {len(conversation_docs)} 个")
    print(f"无效文档: {len(invalid_docs)} 个")
    print()

    if len(conversation_docs) > 0:
        print(f"[WARNING] 发现 {len(conversation_docs)} 个疑似对话记录的文档！")
        print("这些文档会影响RAG检索质量，建议删除。")
        print()
        print("对话记录列表:")
        for doc in conversation_docs:
            print(f"  - {doc.file_name}")
        print()
        print("是否删除这些对话记录？(需要手动确认)")
        print("运行: python cleanup_conversation_docs.py")

    if len(technical_docs) < len(docs) * 0.5:
        print(f"[WARNING] 技术文档占比低于50%，知识库质量较差！")
        print("建议上传更多高质量的技术文档。")

if __name__ == "__main__":
    main()
