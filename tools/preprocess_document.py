"""
文档预处理工具 - 清理文档，提升质量
"""

import re
from pathlib import Path


def clean_text(text: str) -> str:
    """
    清理文本内容

    Args:
        text: 原始文本

    Returns:
        str: 清理后的文本
    """
    # 移除多余空白
    text = re.sub(r'\n{3,}', '\n\n', text)  # 多余空行
    text = re.sub(r' +', ' ', text)  # 多余空格

    # 移除特殊符号（可选）
    text = re.sub(r'[@#$%^&*]{3,}', '', text)  # 连续特殊符号

    # 统一引号
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    # 移除页眉页脚
    text = re.sub(r'第\d+页', '', text)
    text = re.sub(r'Page \d+', '', text)

    # 去除首尾空白
    text = text.strip()

    return text


def check_quality(text: str) -> dict:
    """
    检查文档质量

    Args:
        text: 文档内容

    Returns:
        dict: 质量检查报告
    """
    issues = []

    # 检查 1：内容长度
    if len(text) < 100:
        issues.append("❌ 内容太短，少于100字符")
    elif len(text) < 500:
        issues.append("⚠️ 内容较少，建议增加更多内容")
    else:
        issues.append("✅ 内容长度合适")

    # 检查 2：特殊字符
    special_chars = re.findall(r'[@#$%^&*]{3,}', text)
    if special_chars:
        issues.append(f"❌ 发现 {len(special_chars)} 处特殊符号")
    else:
        issues.append("✅ 没有异常特殊符号")

    # 检查 3：乱码检测
    if '\ufffd' in text:
        issues.append("❌ 发现替换字符（可能有乱码）")
    else:
        issues.append("✅ 没有明显乱码")

    # 检查 4：段落长度
    paragraphs = text.split('\n\n')
    long_paragraphs = [p for p in paragraphs if len(p) > 1000]
    if long_paragraphs:
        issues.append(f"⚠️ 有 {len(long_paragraphs)} 个超长段落（>1000字符）")
    else:
        issues.append("✅ 段落长度合理")

    # 检查 5：空内容
    if not text.strip():
        issues.append("❌ 文档为空")

    return {
        'issues': issues,
        'is_good': all('✅' in issue for issue in issues if issue.startswith('✅') or issue.startswith('⚠️'))
    }


def preprocess_file(file_path: str, output_path: str = None) -> str:
    """
    预处理文件

    Args:
        file_path: 输入文件路径
        output_path: 输出文件路径（可选）

    Returns:
        str: 清理后的文本
    """
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 清理文本
    cleaned_text = clean_text(text)

    # 质量检查
    report = check_quality(cleaned_text)

    print("=" * 50)
    print(f"文档质量检查报告: {file_path}")
    print("=" * 50)
    for issue in report['issues']:
        print(issue)
    print("=" * 50)

    # 保存文件
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        print(f"✅ 清理后的文件已保存: {output_path}")

    return cleaned_text


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python preprocess_document.py <文件路径> [输出路径]")
        print("示例: python preprocess_document.py input.md output.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not output_file:
        # 自动生成输出文件名
        path = Path(input_file)
        output_file = str(path.parent / f"{path.stem}_cleaned{path.suffix}")

    preprocess_file(input_file, output_file)
