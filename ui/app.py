"""
AI 知识库问答系统 - 主界面
"""

import streamlit as st
import sys
import os

# 添加项目路径（ui 目录的上一级是项目根目录）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStoreManager
from src.llm.llm_client import OllamaClient
from src.rag import RAGChain
from src.config import settings
from src.utils.logger import setup_logger

# 页面配置
st.set_page_config(
    page_title="AI 知识库",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化日志
setup_logger(log_level="INFO")

# 初始化会话状态
if 'rag_chain' not in st.session_state:
    with st.spinner("正在初始化系统..."):
        # 初始化组件
        metadata_store = MetadataStore(settings.metadata_db)
        vector_store = VectorStoreManager(settings.vector_store_dir)
        llm_client = OllamaClient()

        # 检查 Ollama 连接
        if llm_client.check_connection():
            st.session_state.ollama_connected = True
            st.success("✅ LLM 服务连接成功")
        else:
            st.session_state.ollama_connected = False
            st.error("❌ 无法连接到 Ollama 服务，请先运行: ollama serve")

        # 创建 RAG 链路
        st.session_state.rag_chain = RAGChain(
            vector_store=vector_store,
            llm_client=llm_client,
            metadata_store=metadata_store,
            min_similarity=settings.min_similarity
        )

        st.session_state.model = settings.ollama_model

# 侧边栏
with st.sidebar:
    st.title("📚 AI 知识库 v1.0")
    st.markdown("---")

    # 统计信息
    docs = st.session_state.rag_chain.metadata_store.list_documents()
    active_docs = [d for d in docs if d.status.value == 'active']

    st.metric("📄 文档数量", len(active_docs))

    vector_stats = st.session_state.rag_chain.vector_store.get_stats()
    st.metric("🔢 向量数量", vector_stats['total_count'])

    st.markdown("---")
    st.markdown("### 📊 系统状态")

    if st.session_state.get('ollama_connected'):
        st.success("✅ LLM 服务正常")
    else:
        st.error("❌ LLM 服务未连接")

    st.caption(f"🤖 模型: {st.session_state.get('model', 'llama3:8b')}")

    st.markdown("---")
    st.markdown("### 📜 问答历史")

    # 获取历史记录
    chat_history = st.session_state.rag_chain.metadata_store.get_chat_history(limit=10)

    if chat_history:
        st.caption(f"共 {len(chat_history)} 条记录")

        # 显示最近的历史记录
        for i, chat in enumerate(chat_history):
            with st.expander(f"Q: {chat['question'][:40]}...", key=f"history_{i}"):
                st.markdown(f"**问题:** {chat['question']}")
                st.markdown(f"**答案:** {chat['answer']}")
                st.caption(f"⏰ {chat['timestamp']}")

        # 清空历史按钮
        if st.button("🗑️ 清空历史", key="clear_history"):
            if st.session_state.rag_chain.metadata_store.clear_chat_history():
                st.success("历史记录已清空")
                st.rerun()
            else:
                st.error("清空失败")
    else:
        st.caption("暂无历史记录")

    st.markdown("---")
    st.markdown("### 📂 功能导航")

    page = st.radio(
        "选择功能",
        ["💬 问答", "📄 文档管理", "🐛 调试"],
        label_visibility="collapsed"
    )

# 主页面
if page == "💬 问答":
    st.title("💬 智能问答")

    st.markdown("""
    使用说明：
    1. 先在"文档管理"页面上传文档
    2. 然后在这里提问，系统会基于文档内容回答
    """)

    if not active_docs:
        st.info("👉 知识库为空，请先上传文档")
    else:
        # 问答界面
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # 显示历史消息
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

                # 显示来源
                if message.get('sources'):
                    with st.expander("📚 检索来源"):
                        for source in message['sources']:
                            st.caption(f"📄 {source['source_name']} [相似度: {source['similarity']:.2f}]")

        # 输入框
        if prompt := st.chat_input("输入你的问题..."):
            # 显示用户消息
            st.session_state.messages.append({
                'role': 'user',
                'content': prompt
            })
            with st.chat_message('user'):
                st.markdown(prompt)

            # 生成回答
            with st.chat_message('assistant'):
                with st.spinner('🤔 思考中...'):
                    result = st.session_state.rag_chain.ask(prompt)

                st.markdown(result['answer'])

                if result.get('sources'):
                    with st.expander("📚 检索来源"):
                        for source in result['sources']:
                            st.caption(f"📄 {source['source_name']} [相似度: {source['similarity']:.2f}]")

            # 保存到历史（内存）
            st.session_state.messages.append({
                'role': 'assistant',
                'content': result['answer'],
                'sources': result.get('sources', []),
                'metadata': result.get('metadata', {})
            })

            # 保存到数据库
            st.session_state.rag_chain.metadata_store.save_chat(
                question=prompt,
                answer=result['answer'],
                sources=result.get('sources', [])
            )

elif page == "📄 文档管理":
    st.title("📄 文档管理")

    st.markdown("---")

    # 上传区域
    st.subheader("📤 上传文档")

    col1, col2 = st.columns(2)

    with col1:
        uploaded_files = st.file_uploader(
            "选择文档（支持批量）",
            type=['pdf', 'md', 'txt'],
            accept_multiple_files=True,
            help="支持 PDF、Markdown、纯文本，可一次选择多个文件"
        )

    with col2:
        if uploaded_files:
            st.info(f"已选择 {len(uploaded_files)} 个文件")

            # 显示文件列表
            total_size = sum(f.size for f in uploaded_files)
            st.caption(f"总大小: {total_size / 1024:.2f} KB")

            for f in uploaded_files:
                st.caption(f"📄 {f.name} ({f.size / 1024:.2f} KB)")

            if st.button("🚀 开始处理", type="primary"):
                # 保存文件
                import tempfile
                import shutil

                # 创建临时目录
                temp_dir = tempfile.mkdtemp()

                # 处理结果统计
                success_count = 0
                failed_count = 0
                results = []

                # 创建进度条
                progress_bar = st.progress(0, text="准备处理...")

                for i, uploaded_file in enumerate(uploaded_files):
                    # 更新进度
                    progress = (i) / len(uploaded_files)
                    progress_bar.progress(progress, text=f"正在处理: {uploaded_file.name} ({i+1}/{len(uploaded_files)})")

                    # 保存文件
                    file_path = os.path.join(temp_dir, uploaded_file.name)

                    try:
                        with open(file_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())

                        # 处理文档
                        result = st.session_state.rag_chain.add_document(file_path)

                        if result['success']:
                            success_count += 1
                            results.append({
                                'file': uploaded_file.name,
                                'status': 'success',
                                'message': result['message'],
                                'chunks': result.get('chunk_count', 0)
                            })
                        else:
                            failed_count += 1
                            results.append({
                                'file': uploaded_file.name,
                                'status': 'failed',
                                'message': result['message']
                            })

                    except Exception as e:
                        failed_count += 1
                        results.append({
                            'file': uploaded_file.name,
                            'status': 'error',
                            'message': f"处理异常: {str(e)}"
                        })

                # 完成进度
                progress_bar.progress(1.0, text="处理完成！")

                # 显示结果汇总
                st.markdown("---")
                st.subheader("📊 处理结果汇总")

                col1, col2, col3 = st.columns(3)
                col1.metric("✅ 成功", success_count)
                col2.metric("❌ 失败", failed_count)
                col3.metric("📄 总计", len(uploaded_files))

                # 显示详细结果
                st.markdown("---")
                for result in results:
                    if result['status'] == 'success':
                        st.success(f"✅ {result['file']}")
                        st.caption(f"   {result['message']}")
                    else:
                        st.error(f"❌ {result['file']}")
                        st.caption(f"   {result['message']}")

                # 清理临时文件
                shutil.rmtree(temp_dir)

                # 刷新页面
                if success_count > 0:
                    st.rerun()

    st.markdown("---")

    # 文档列表
    st.subheader("📋 文档列表")

    if not docs:
        st.info("暂无文档")
    else:
        # 按状态分组显示
        active_docs = [d for d in docs if d.status.value == 'active']
        indexing_docs = [d for d in docs if d.status.value == 'indexing']
        failed_docs = [d for d in docs if d.status.value == 'failed']

        if active_docs:
            st.markdown("### ✅ 活跃文档")
            for doc in active_docs:
                with st.expander(f"📄 {doc.file_name}"):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("类型", doc.file_type)
                    col2.metric("大小", f"{doc.file_size / 1024:.1f} KB")
                    col3.metric("块数", doc.chunk_count)
                    col4.metric("状态", doc.status.value)

                    if st.button(f"🗑️ 删除", key=f"delete_{doc.source_id}"):
                        result = st.session_state.rag_chain.delete_document(doc.source_id)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()

        if indexing_docs:
            st.markdown("### ⏳ 处理中")
            for doc in indexing_docs:
                st.caption(f"📄 {doc.file_name} - 正在处理...")

        if failed_docs:
            st.markdown("### ❌ 失败文档")
            for doc in failed_docs:
                with st.expander(f"📄 {doc.file_name}"):
                    st.write(f"**错误信息:** {doc.error_message}")
                    st.caption(f"Source ID: {doc.source_id}")

elif page == "🐛 调试":
    st.title("🐛 调试面板")

    st.markdown("""
    这里会显示系统的调试信息，包括：
    - 日志输出
    - 统计信息
    - 配置参数
    """)

    st.markdown("---")

    # 系统配置
    st.subheader("⚙️ 系统配置")

    st.json({
        "ollama_base_url": settings.ollama_base_url,
        "ollama_model": settings.ollama_model,
        "embedding_model": settings.embedding_model,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "top_k_results": settings.top_k_results,
        "min_similarity": settings.min_similarity
    })

    st.markdown("---")

    # 统计信息
    st.subheader("📊 统计信息")

    st.json({
        "total_documents": len(docs),
        "active_documents": len(active_docs),
        "total_vectors": vector_stats['total_count'],
        "ollama_connected": st.session_state.get('ollama_connected', False)
    })

    st.markdown("---")

    # 日志查看
    st.subheader("📝 日志")

    log_file = settings.log_file
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.readlines()
            # 显示最后 20 行
            for line in logs[-20:]:
                st.text(line)
    else:
        st.info(f"日志文件不存在: {log_file}")
