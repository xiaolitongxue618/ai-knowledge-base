#!/usr/bin/env python3
"""
快速启动脚本 - 运行测试或启动应用
"""

import sys
import os
import subprocess

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print(" 📚 AI 知识库问答系统 v1.0")
    print("=" * 60)
    print()

def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    print()

    # 测试元数据存储
    print("1️⃣  元数据存储测试")
    os.system("python tests/test_metadata_store.py")
    print()

    # 测试文档解析
    print("2️⃣  文档解析测试")
    os.system("python tests/test_document_processing.py")
    print()

    print("✅ 所有测试完成！")

def start_app():
    """启动应用"""
    print("🚀 启动 Streamlit 应用...")
    print()

    # 检查 Ollama
    print("🔍 检查 Ollama 服务...")
    try:
        import ollama
        client = ollama.Client()
        client.list()
        print("✅ Ollama 服务正常")
    except:
        print("❌ 无法连接到 Ollama 服务")
        print("   请先在新终端运行: ollama serve")
        return

    print()
    print("📝 启动应用...")
    print("   应用将在 http://localhost:8501 启动")
    print("   按 Ctrl+C 停止")
    print()

    os.system("streamlit run ui/app.py")

def main():
    """主函数"""
    print_banner()

    print("请选择操作:")
    print("  1. 运行测试")
    print("  2. 启动应用")
    print("  3. 退出")
    print()

    choice = input("请输入选项 (1/2/3): ").strip()

    if choice == "1":
        run_tests()
    elif choice == "2":
        start_app()
    elif choice == "3":
        print("👋 再见！")
    else:
        print("❌ 无效选项")

if __name__ == "__main__":
    main()
