# Claude 开发指南 - AI 知识库项目

> 本文档为Claude AI助手提供项目上下文和开发规范

## 项目概述

**项目名称**：AI 知识库问答系统
**项目类型**：RAG（检索增强生成）学习项目 + 实用工具
**技术栈**：Python 3.10+ / Streamlit / Ollama / ChromaDB / SQLite
**部署地址**：http://43.128.97.2:8501
**GitHub仓库**：https://github.com/xiaolitongxue618/ai-knowledge-base

### 核心功能

- ✅ 文档上传（PDF/Markdown/纯文本，支持批量）
- ✅ 智能问答（RAG架构，展示来源引用）
- ✅ 文档管理（搜索、过滤、删除）
- ✅ 问答历史（持久化存储）
- ✅ 导出功能（Markdown格式）
- ✅ 调试面板（系统配置和日志）

---

## 设计系统 ⭐ 重要

**必须阅读**：所有UI/UX决策必须遵循 [[DESIGN.md]]

### 设计风格：Apple极简主义

**核心原则**：
- **极致极简** — 去除一切不必要的装饰
- **字体优先** — 系统字体，17px标准正文
- **宽松留白** — 慷慨的间距，让内容呼吸
- **唯一强调色** — Apple Blue (#0071E3)，仅在交互时使用
- **微妙阴影** — 不用边框，用深度分隔

### 关键规范

| 设计元素 | 规格 | 说明 |
|---------|------|------|
| 主色 | `#0071E3` | Apple Blue，仅用于交互 |
| 背景 | `#FFFFFF` / `#F5F5F7` | 纯白或浅灰 |
| 正文 | 17px | Apple标准，比业界16px稍大 |
| 圆角 | 10-12px | Apple标准（业界6-8px） |
| 间距 | 宽松 | 奢华的呼吸感 |
| 阴影 | 极微妙 | 0 1px 3px rgba(0,0,0,0.04) |
| 动效 | 300-400ms | 比业界慢，从容不迫 |

### 严禁事项

- ❌ 不使用渐变
- ❌ 不使用紫色/靛蓝/暖灰色
- ❌ 不使用小圆角（6-8px）
- ❌ 不使用快速动画（<200ms）
- ❌ 不过度装饰

---

## 项目结构

```
ai-knowledge-base/
├── data/                          # 数据目录
│   ├── documents/                 # 原始文档存储
│   ├── vector_store/              # ChromaDB向量数据库
│   └── metadata/                  # SQLite元数据库
│
├── src/                           # 核心代码
│   ├── config.py                  # 配置管理
│   ├── processors/                # 文档处理
│   │   ├── document_processor.py
│   │   └── text_splitter.py
│   ├── storage/                   # 存储层
│   │   ├── vector_store.py        # ChromaDB封装
│   │   └── metadata_store.py      # SQLite封装
│   ├── llm/                       # LLM客户端
│   │   └── llm_client.py          # Ollama封装
│   ├── rag/                       # RAG链路
│   │   └── rag_chain.py           # 核心问答逻辑
│   └── utils/                     # 工具函数
│       └── logger.py
│
├── ui/                            # Streamlit界面
│   └── app.py                     # 主应用入口
│
├── tools/                         # 工具脚本
│   └── preprocess_document.py     # 文档预处理
│
├── logs/                          # 日志目录
│
├── 00.操作手册/                   # 文档
│   └── 完整操作手册.md
│
├── 02.开发日志/                   # 开发记录
│   ├── 001-013.md                 # 各阶段记录
│   └── ...
│
├── DESIGN.md                      # ⭐ 设计系统
├── CLAUDE.md                      # 本文件
├── requirements.txt               # Python依赖
├── ecosystem.config.json          # PM2配置
├── start_streamlit.sh             # 启动脚本
├── .env                           # 环境变量（本地）
└── README.md                      # 项目说明
```

---

## 技术架构

### RAG流程

```
文档上传 → 解析提取 → 文本切分 → 向量化 → 存储
                                               ↓
用户提问 → 向量化 → 检索(Top-K) → 排序(相似度) → LLM生成 → 返回答案+来源
```

### 关键组件

**1. 文档处理器（document_processor.py）**
- 支持PDF（PyPDF2）、Markdown、纯文本
- MD5去重（source_id）
- 状态机：indexing → active/failed

**2. 向量存储（vector_store.py）**
- ChromaDB持久化
- 余弦距离（cosine）
- 相似度公式：`1 - (distance / 2)`
- Top-K检索（默认3-5个结果）

**3. LLM客户端（llm_client.py）**
- Ollama集成
- 模型：qwen2.5:0.5b（量化版本，397MB）
- Embedding：nomic-embed-text（768维）

**4. 元数据存储（metadata_store.py）**
- SQLite持久化
- 表：documents, chat_history
- 索引优化（source_id, timestamp）

**5. RAG链路（rag_chain.py）**
- 协调所有组件
- 最小相似度阈值：0.5
- Prompt工程（中文优化）

---

## 配置说明

### 环境变量（.env）

```bash
# Ollama配置
OLLAMA_BASE_URL=http://localhost:11414
OLLAMA_MODEL=qwen2.5:0.5b
EMBEDDING_MODEL=nomic-embed-text

# 向量存储
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=3
MIN_SIMILARITY=0.5

# 路径
VECTOR_STORE_DIR=./data/vector_store
METADATA_DB=./data/metadata/knowledge_base.db
LOG_FILE=./logs/app.log
```

### Streamlit配置（.streamlit/config.toml）

```toml
[theme]
primaryColor = "#0071E3"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F7"
textColor = "#1D1D1F"
font = "sans serif"

[client]
showErrorDetails = false
maxUploadSize = 200

[server]
headless = true
port = 8501
```

---

## 部署架构

### 服务器环境

- **位置**：腾讯云新加坡
- **IP**：43.128.97.2
- **端口**：8501（Streamlit）
- **系统**：Ubuntu 24.04
- **内存**：3.6GB（总）
- **Python**：3.12（虚拟环境）

### 进程管理（PM2）

```bash
# 查看状态
pm2 status

# 查看日志
pm2 logs ai-kb

# 重启
pm2 restart ai-kb

# 停止
pm2 stop ai-kb
```

**PM2配置文件**：[[ecosystem.config.json]]
**启动脚本**：[[start_streamlit.sh]]

### 服务开机自启

```bash
# PM2服务
sudo systemctl status pm2-ubuntu

# Ollama服务
sudo systemctl status ollama
```

---

## 开发规范

### 代码风格

- **Python**：遵循PEP 8
- **类型提示**：使用Python 3.10+类型注解
- **文档字符串**：Google风格
- **日志**：使用`src/utils/logger.py`，不使用`print()`

### Git提交

```bash
# 提交前检查
- 代码通过测试
- 无硬编码路径
- 环境变量在.env中定义
- 更新相关文档

# 提交信息格式
feat: 添加批量上传功能
fix: 修复相似度计算错误
docs: 更新部署文档
refactor: 重构向量存储层
```

### 测试

```bash
# 运行测试（如果有）
python -m pytest tests/

# 手动测试流程
1. 启动Ollama: ollama serve
2. 启动应用: streamlit run ui/app.py
3. 上传测试文档
4. 验证问答质量
5. 检查来源引用准确性
```

---

## 故障排查

### 常见问题

**1. Ollama连接失败**
```bash
# 检查服务状态
ollama list

# 重启Ollama
ollama serve

# 验证模型
ollama pull qwen2.5:0.5b
```

**2. 向量相似度为负数**
- 原因：使用L2距离而非余弦距离
- 解决：检查`src/storage/vector_store.py`中的metadata配置

**3. Streamlit进程停止**
```bash
# 检查PM2状态
pm2 status

# 查看错误日志
pm2 logs ai-kb --err

# 重启服务
pm2 restart ai-kb
```

**4. 内存不足**
- 症状：进程频繁重启
- 解决：使用小模型（qwen2.5:0.5b），增加PM2的`max_memory_restart`

---

## 开发里程碑

- ✅ **Milestone 1**：核心功能（文档上传、RAG问答）
- ✅ **Milestone 2**：服务器部署（PM2进程守护）
- ✅ **Milestone 3**：功能完善（批量上传、搜索过滤、导出）
- 🔄 **当前**：UI/UX优化（Apple风格设计系统）

**下一步**：
- [ ] 实施Apple风格设计到Streamlit界面
- [ ] 添加更多文档格式支持（DOCX、PPT）
- [ ] 实现文档分类和标签
- [ ] 添加用户认证（可选）

---

## 学习资源

- [RAG论文原文](https://arxiv.org/abs/2005.11401)
- [Ollama文档](https://ollama.com/docs)
- [ChromaDB文档](https://docs.trychroma.com/)
- [Streamlit文档](https://docs.streamlit.io/)
- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/)

---

## 最后更新

**日期**：2026-03-25
**更新内容**：添加Apple风格设计系统规范
**版本**：v1.0

---

**重要提醒**：
1. ⭐ **任何UI修改前必须阅读 DESIGN.md**
2. 🔧 **修改配置后记得更新.env和config.py**
3. 📝 **重大修改需要更新CLAUDE.md**
4. 🚀 **部署前在本地充分测试**
