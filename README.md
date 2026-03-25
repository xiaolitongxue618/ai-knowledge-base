# AI 知识库问答系统

> 从零到一构建工业级AI知识库的学习项目

## 📋 项目简介

这是一个通过实战学习RAG（检索增强生成）技术的项目。目标是构建一个能够上传文档、智能问答、展示来源的AI知识库系统。

### 学习目标

- ✅ 掌握 RAG 系统的核心原理
- ✅ 学习向量数据库的使用
- ✅ 理解 LLM 应用开发的关键技术
- ✅ 实践 Prompt Engineering
- ✅ 建立工业级代码规范

## 🎯 功能特性

### v1.0（当前版本）

- ✅ 支持上传 PDF/Markdown/纯文本文档
- ✅ 智能问答，展示检索来源
- ✅ 文档管理（上传、列表、删除）
- ✅ 调试面板（查看Prompt、检索结果）
- ✅ 文档状态管理（indexing → active/failed）

### 技术栈

| 组件 | 技术选型 |
|------|---------|
| 开发语言 | Python 3.10+ |
| LLM | Ollama + Llama3 8B |
| 向量数据库 | ChromaDB |
| 前端 | Streamlit |
| 元数据库 | SQLite |

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Ollama（本地运行LLM）
- 16GB+ 内存（推荐32GB）
- 可选：NVIDIA GPU（加速）

### 安装步骤

#### 1. 安装 Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
从 [ollama.com](https://ollama.com/download) 下载安装

#### 2. 启动 Ollama 并下载模型

```bash
# 新开一个终端，启动 Ollama
ollama serve

# 另一个终端，下载模型
ollama pull llama3:8b
ollama pull nomic-embed-text
```

#### 3. 安装项目依赖

```bash
# 克隆项目（或进入项目目录）
cd ai-knowledge-base

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件（可选，有默认值）
```

#### 5. 运行应用

```bash
streamlit run ui/app.py
```

应用将在 `http://localhost:8501` 启动。

## 📂 项目结构

```
ai-knowledge-base/
├── data/                  # 数据目录
│   ├── documents/        # 原始文档
│   ├── vector_store/     # ChromaDB 持久化
│   └── metadata/         # SQLite 数据库
├── src/                  # 源代码
│   ├── config.py         # 配置管理
│   ├── processors/       # 文档处理
│   ├── storage/          # 存储模块
│   ├── llm/              # LLM 客户端
│   └── rag/              # RAG 链路
├── ui/                   # Streamlit 界面
├── tests/                # 测试
├── requirements.txt      # 依赖清单
└── README.md            # 本文件
```

## 🔧 开发状态

### Milestone 1: 环境搭建与文档摄入 ⏳ 进行中

- [x] 项目目录结构
- [ ] 配置文件（requirements.txt, .env）
- [ ] 文档解析模块（PDF/MD/TXT）
- [ ] 文本分块功能
- [ ] ChromaDB 集成
- [ ] 元数据存储（SQLite）

### Milestone 2: 核心问答功能 📋 计划中

- [ ] LLM 客户端（Ollama 集成）
- [ ] RAG 问答链路
- [ ] 问答界面
- [ ] 调试面板

### Milestone 3: 评测与优化 📋 计划中

- [ ] 基准问答集
- [ ] 评测脚本
- [ ] 性能优化

### Milestone 4: 完善与部署准备 📋 计划中

- [ ] 单元测试
- [ ] 文档完善
- [ ] 使用示例

## 📚 学习资源

- [Ollama 文档](https://ollama.com/docs)
- [ChromaDB 文档](https://docs.trychroma.com/)
- [RAG 论文](https://arxiv.org/abs/2005.11401)

## 📝 开发日志

- [环境搭建踩坑记](./02.开发日志/001.环境搭建踩坑记.md) - 待写
- [文档解析实战](./02.开发日志/002.文档解析实战.md) - 待写

## 🤝 贡献

这是一个学习项目，欢迎提Issue和PR！

## 📄 许可证

MIT License

---

**项目版本：** v1.0
**最后更新：** 2026-03-25
**学习进度：** Milestone 1 进行中
