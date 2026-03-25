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

# Liquid Glass 液态玻璃风格自定义CSS（优化版）
liquid_glass_css = """
<style>
    /* ==================== 全局背景动画 ==================== */
    .stApp {
        background: linear-gradient(135deg, #F5F5F7 0%, #E8E8ED 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientFlow 15s ease infinite !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
                     "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif !important;
        font-size: 19px !important;
        font-weight: 500 !important;
        line-height: 1.5 !important;
        letter-spacing: -0.01em !important;
        -webkit-font-smoothing: antialiased !important;
    }

    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ==================== 主页面顶部间距优化 ==================== */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }

    /* ==================== 侧边栏按钮间距优化 ==================== */
    .stSidebar button[kind="default"] {
        margin-bottom: 6px !important;
    }

    /* ==================== 毛玻璃卡片基础 ==================== */
    .glass-card {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(30px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow:
            0 8px 32px rgba(0, 113, 227, 0.12),
            0 0 0 1px rgba(255, 255, 255, 0.6) inset !important;
        transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
    }

    /* ==================== 标题 ==================== */
    h1 {
        font-size: 40px !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        line-height: 1.1 !important;
        background: linear-gradient(135deg, #0071E3 0%, #5856D6 50%, #AF52DE 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        background-size: 200% 200% !important;
        animation: gradientText 8s ease infinite !important;
    }

    @keyframes gradientText {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    h2 {
        font-size: 32px !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
        line-height: 1.2 !important;
        background: linear-gradient(135deg, #0071E3, #5856D6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }

    h3 {
        font-size: 26px !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.25 !important;
    }

    /* ==================== 液态玻璃按钮 ==================== */
    .stButton > button {
        border-radius: 9999px !important;
        padding: 16px 32px !important;
        font-size: 19px !important;
        font-weight: 600 !important;
        transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
        border: none !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0071E3 0%, #5856D6 100%) !important;
        background-size: 200% 200% !important;
        color: white !important;
        box-shadow:
            0 4px 16px rgba(0, 113, 227, 0.3),
            inset 0 1px 1px rgba(255, 255, 255, 0.3) !important;
        animation: btnGradient 6s ease infinite !important;
    }

    @keyframes btnGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ==================== 次要按钮（毛玻璃样式） ==================== */
    .stButton > button:not([kind="primary"]) {
        background: rgba(235, 240, 250, 0.8) !important;
        backdrop-filter: blur(25px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(25px) saturate(200%) !important;
        border: 1px solid rgba(200, 210, 230, 0.8) !important;
        color: #1D1D1F !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        box-shadow:
            0 2px 8px rgba(0, 113, 227, 0.08),
            inset 0 1px 2px rgba(255, 255, 255, 0.6) !important;
        transition: background 0.2s ease, box-shadow 0.2s ease !important;
    }

    /* 悬停状态 - 明显的蓝色 */
    .stButton > button:not([kind="primary"]):hover {
        background: rgba(100, 150, 255, 0.25) !important;
        border-color: rgba(0, 113, 227, 0.5) !important;
        box-shadow:
            0 4px 12px rgba(0, 113, 227, 0.2),
            inset 0 1px 2px rgba(255, 255, 255, 0.7) !important;
    }

    /* 点击状态 - 更深的蓝色 */
    .stButton > button:not([kind="primary"]):active {
        background: rgba(0, 113, 227, 0.3) !important;
        border-color: rgba(0, 113, 227, 0.7) !important;
        box-shadow:
            0 2px 6px rgba(0, 113, 227, 0.3),
            inset 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }

    /* 针对导航按钮的特定样式 */
    button[data-key="nav_chat"]:hover,
    button[data-key="nav_docs"]:hover,
    button[data-key="nav_debug"]:hover {
        background: rgba(100, 150, 255, 0.3) !important;
        border-color: rgba(0, 113, 227, 0.6) !important;
    }

    button[data-key="nav_chat"]:active,
    button[data-key="nav_docs"]:active,
    button[data-key="nav_debug"]:active {
        background: rgba(0, 113, 227, 0.4) !important;
        border-color: rgba(0, 113, 227, 0.8) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0071E3 0%, #5856D6 50%, #AF52DE 100%) !important;
        box-shadow:
            0 6px 20px rgba(0, 113, 227, 0.5),
            inset 0 1px 1px rgba(255, 255, 255, 0.5) !important;
    }

    .stButton > button[kind="primary"]:active {
        background: linear-gradient(135deg, #0050C5 0%, #4836A6 50%, #8F3CB8 100%) !important;
        box-shadow:
            0 4px 12px rgba(0, 113, 227, 0.6),
            inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
    }

    .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: #0071E3 !important;
        box-shadow:
            0 2px 8px rgba(0, 113, 227, 0.1),
            inset 0 1px 1px rgba(255, 255, 255, 0.5) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        box-shadow:
            0 4px 12px rgba(0, 113, 227, 0.15),
            inset 0 1px 1px rgba(255, 255, 255, 0.6) !important;
    }

    /* ==================== 毛玻璃输入框 ==================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 18px !important;
        border: 1px solid rgba(0, 113, 227, 0.3) !important;
        padding: 16px 24px !important;
        font-size: 19px !important;
        font-weight: 500 !important;
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        transition: all 0.4s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.5) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border: 2px solid !important;
        border-image: linear-gradient(135deg, #0071E3, #5856D6) 1 !important;
        box-shadow:
            0 0 0 6px rgba(0, 113, 227, 0.15),
            inset 0 1px 1px rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
    }

    /* ==================== 毛玻璃卡片 ==================== */
    .stMetric {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(30px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 24px !important;
        padding: 24px !important;
        box-shadow:
            0 8px 32px rgba(0, 113, 227, 0.12),
            0 0 0 1px rgba(255, 255, 255, 0.5) inset !important;
        transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
    }

    .stMetric:hover {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(35px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(35px) saturate(200%) !important;
        box-shadow:
            0 12px 40px rgba(0, 113, 227, 0.16),
            0 0 0 1px rgba(255, 255, 255, 0.7) inset !important;
    }

    /* ==================== 毛玻璃文件上传器 ==================== */
    .stFileUploader {
        border: 2px dashed rgba(0, 113, 227, 0.4) !important;
        border-radius: 32px !important;
        padding: 96px 48px !important;
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
    }

    .stFileUploader:hover {
        border-style: solid !important;
        border-color: #5856D6 !important;
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
    }

    /* ==================== 毛玻璃展开器 ==================== */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(30px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 24px !important;
        padding: 20px 24px !important;
        font-weight: 600 !important;
        transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(35px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(35px) saturate(200%) !important;
    }

    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        padding: 24px !important;
        margin-top: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    /* ==================== 毛玻璃聊天消息 ==================== */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(30px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 32px !important;
        padding: 20px 24px !important;
        box-shadow:
            0 4px 16px rgba(0, 113, 227, 0.1),
            0 0 0 1px rgba(255, 255, 255, 0.6) inset !important;
    }

    /* ==================== 进度条 ==================== */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #0071E3 0%, #5856D6 100%) !important;
        background-size: 200% 200% !important;
        animation: btnGradient 6s ease infinite !important;
        border-radius: 9999px !important;
    }

    /* ==================== 侧边栏 ==================== */
    .css-1d391kg, .css-1lcbmhc {
        background: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    /* 侧边栏 - 减少间距 */
    .css-1d391kg h1, .css-1lcbmhc h1 {
        margin-top: 8px !important;
        margin-bottom: 16px !important;
    }

    .css-1d391kg [data-testid="stMetricContainer"], .css-1lcbmhc [data-testid="stMetricContainer"] {
        margin-bottom: 8px !important;
        padding: 12px !important;
    }

    .css-1d391kg .stMarkdown, .css-1lcbmhc .stMarkdown {
        margin-top: 8px !important;
        margin-bottom: 8px !important;
    }

    /* Expander 更紧凑 */
    .css-1d391kg .streamlit-expanderHeader, .css-1lcbmhc .streamlit-expanderHeader {
        padding: 12px 16px !important;
        margin-bottom: 4px !important;
    }

    /* 按钮更紧凑 */
    .css-1d391kg button, .css-1lcbmhc button {
        margin-bottom: 4px !important;
        padding: 8px 16px !important;
    }

    /* ==================== 分割线 ==================== */
    hr {
        border-color: rgba(255, 255, 255, 0.2) !important;
        margin: 32px 0 !important;
    }

    /* ==================== 标签 ==================== */
    .stBadge {
        border-radius: 14px !important;
        padding: 8px 16px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
</style>
"""

st.markdown(liquid_glass_css, unsafe_allow_html=True)

# 初始化日志
setup_logger(log_level="INFO")

# 初始化会话状态
if 'rag_chain' not in st.session_state:
    with st.spinner("正在初始化系统..."):
        try:
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
                st.stop()

            # 创建 RAG 链路
            st.session_state.rag_chain = RAGChain(
                vector_store=vector_store,
                llm_client=llm_client,
                metadata_store=metadata_store,
                min_similarity=settings.min_similarity
            )

            st.session_state.model = settings.ollama_model
        except Exception as e:
            st.error(f"❌ 初始化失败: {str(e)}")
            st.stop()

# 侧边栏 - Liquid Glass 液态玻璃（优化间距）
with st.sidebar:
    if 'rag_chain' not in st.session_state:
        st.warning("⚠️ 系统未初始化")
        st.stop()

    # 初始化当前页面
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "问答"

    # ========== 标题（居中，舒适紧凑布局） ==========
    st.markdown("""
    <div style="
        text-align: center;
        padding: 3px 0 5px 0;
        margin-bottom: 4px;
    ">
        <h2 style="
            margin: 0 0 8px 0;
            font-size: 27px;
            font-weight: 800;
            background: linear-gradient(135deg, #0071E3 0%, #5856D6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        ">AI 知识库</h2>
        <div style="display: flex; align-items: center; justify-content: center; gap: 6px;">
            <div style="width: 7px; height: 7px; border-radius: 50%; background: #34C759; box-shadow: 0 0 8px #34C759;"></div>
            <span style="font-size: 11px; color: #86868B; font-weight: 500;">在线</span>
            <span style="font-size: 9px; color: #AEAEB2;">qwen2.5:0.5b</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ========== 导航按钮（竖向，无跳动） ==========
    # 问答按钮
    if st.session_state.current_page == "问答":
        st.markdown("""
        <style>
        button[data-key="nav_chat"] {
            background: linear-gradient(135deg, #0071E3 0%, #5856D6 100%) !important;
            color: white !important;
            font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    if st.button("💬 问答", key="nav_chat", use_container_width=True):
        st.session_state.current_page = "问答"
        st.session_state.show_all_history = False  # 重置历史记录显示状态
        st.rerun()

    # 文档管理按钮
    if st.session_state.current_page == "文档管理":
        st.markdown("""
        <style>
        button[data-key="nav_docs"] {
            background: linear-gradient(135deg, #0071E3 0%, #5856D6 100%) !important;
            color: white !important;
            font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    if st.button("📄 文档管理", key="nav_docs", use_container_width=True):
        st.session_state.current_page = "文档管理"
        st.session_state.show_all_history = False  # 重置历史记录显示状态
        st.rerun()

    # 调试按钮
    if st.session_state.current_page == "调试":
        st.markdown("""
        <style>
        button[data-key="nav_debug"] {
            background: linear-gradient(135deg, #0071E3 0%, #5856D6 100%) !important;
            color: white !important;
            font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    if st.button("🐛 调试", key="nav_debug", use_container_width=True):
        st.session_state.current_page = "调试"
        st.session_state.show_all_history = False  # 重置历史记录显示状态
        st.rerun()

    page = st.session_state.current_page

    # 分隔区（舒适紧凑）
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ========== 统计信息（居中，增加padding） ==========
    try:
        docs = st.session_state.rag_chain.metadata_store.list_documents()
        active_docs = [d for d in docs if d.status.value == 'active']
        vector_stats = st.session_state.rag_chain.vector_store.get_stats()
    except:
        active_docs = []
        vector_stats = {'total_count': 0}

    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.45);
        backdrop-filter: blur(40px) saturate(200%);
        -webkit-backdrop-filter: blur(40px) saturate(200%);
        border-radius: 16px;
        padding: 13px 18px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.65);
        box-shadow:
            0 8px 32px rgba(0, 113, 227, 0.15),
            0 0 0 1px rgba(255, 255, 255, 0.8) inset,
            0 2px 4px rgba(255, 255, 255, 0.5) inset;
        text-align: center;
        position: relative;
        overflow: hidden;
    ">
        <div style="display: flex; justify-content: center; gap: 36px;">
            <div style="text-align: center;">
                <p style="margin: 0; font-size: 26px; font-weight: 800; color: #0071E3;">{len(active_docs)}</p>
                <p style="margin: 4px 0 0 0; font-size: 11px; color: #86868B; font-weight: 600;">文档</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; font-size: 26px; font-weight: 800; color: #5856D6;">{vector_stats['total_count']}</p>
                <p style="margin: 4px 0 0 0; font-size: 11px; color: #86868B; font-weight: 600;">向量</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ========== 历史记录按钮（居中，增强毛玻璃） ==========
    if st.button("📜 查看历史问答", key="view_history", use_container_width=True):
        st.session_state.show_all_history = True
        st.rerun()

    # ========== 操作按钮（竖向，统一间距） ==========
    if st.button("导出问答记录", key="export_md", use_container_width=True):
        try:
            chat_history = st.session_state.rag_chain.metadata_store.get_chat_history(limit=1000)
            if chat_history:
                md_content = f"# 问答历史\n\n导出时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                for i, chat in enumerate(reversed(chat_history), 1):
                    md_content += f"## {i}. {chat['question']}\n\n{chat['answer']}\n\n---\n\n"
                st.download_button("⬇️ 下载", data=md_content,
                                file_name=f"qa_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.md",
                                mime="text/markdown")
        except Exception as e:
            st.error(f"导出失败: {str(e)}")

    if st.button("导出文档列表", key="export_docs", use_container_width=True):
        try:
            docs = st.session_state.rag_chain.metadata_store.list_documents()
            if docs:
                md_content = f"# 文档列表\n\n共 {len(docs)} 个文档\n\n"
                for doc in docs:
                    md_content += f"- {doc.file_name} ({doc.file_type}, {doc.file_size/1024:.1f}KB)\n"
                st.download_button("⬇️ 下载", data=md_content,
                                file_name=f"docs_{__import__('datetime').datetime.now().strftime('%Y%m%d')}.md",
                                mime="text/markdown")
        except Exception as e:
            st.error(f"导出失败: {str(e)}")

    if st.button("🗑️ 清空历史", key="clear_history", use_container_width=True):
        try:
            if st.session_state.rag_chain.metadata_store.clear_chat_history():
                st.success("已清空")
                st.rerun()
        except Exception as e:
            st.error(f"失败: {str(e)}")

# 主页面
if page == "问答":
    if 'rag_chain' not in st.session_state:
        st.warning("⚠️ 系统未初始化，请刷新页面")
        st.stop()

    try:
        docs = st.session_state.rag_chain.metadata_store.list_documents()
        active_docs = [d for d in docs if d.status.value == 'active']
    except Exception as e:
        st.error(f"❌ 获取文档列表失败: {str(e)}")
        active_docs = []

    if not active_docs:
        st.info("知识库为空，请先上传文档")
    else:
        # 初始化messages
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # ========== 历史记录模式（独立页面，不显示标题和输入框） ==========
        if st.session_state.get('show_all_history', False):
            st.markdown("### 📜 历史问答记录")

            # 筛选按钮 - 3列布局
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 全部", key="filter_all", use_container_width=True):
                    st.session_state.history_filter = "all"
                    st.rerun()
            with col2:
                if st.button("📅 今天", key="filter_today", use_container_width=True):
                    st.session_state.history_filter = "today"
                    st.rerun()
            with col3:
                if st.button("📆 本周", key="filter_week", use_container_width=True):
                    st.session_state.history_filter = "week"
                    st.rerun()

            # 搜索框独立一行
            search_keyword = st.text_input("🔍 搜索历史记录", placeholder="输入关键词搜索...", key="search_history")

            try:
                # 获取所有历史问答
                all_history = st.session_state.rag_chain.metadata_store.get_chat_history(limit=1000)

                # 筛选逻辑
                import datetime
                from datetime import timedelta

                filtered_history = []
                today = datetime.datetime.now().date()
                week_ago = today - datetime.timedelta(days=7)

                for chat in all_history:
                    # 筛选
                    if st.session_state.get('history_filter') == 'today':
                        chat_date = datetime.datetime.fromisoformat(chat['timestamp']).date()
                        if chat_date != today:
                            continue
                    elif st.session_state.get('history_filter') == 'week':
                        chat_date = datetime.datetime.fromisoformat(chat['timestamp']).date()
                        if chat_date < week_ago:
                            continue

                    # 关键词搜索
                    if search_keyword:
                        if search_keyword.lower() not in chat['question'].lower():
                            continue

                    filtered_history.append(chat)

                if not filtered_history:
                    st.info("没有找到匹配的历史记录")
                    if st.button("返回"):
                        st.session_state.show_all_history = False
                        st.rerun()
                else:
                    # 显示历史问答列表
                    for idx, chat in enumerate(filtered_history):
                        with st.expander(
                            f"**Q:** {chat['question'][:60]}{'...' if len(chat['question']) > 60 else ''}",
                            expanded=False,
                            key=f"history_item_{idx}"
                        ):
                            # 显示问题
                            st.markdown(f"**问题：** {chat['question']}")
                            st.markdown(f"**时间：** {chat['timestamp']}")
                            st.markdown("---")
                            st.markdown(f"**答案：** {chat['answer']}")

            except Exception as e:
                st.error(f"加载历史记录失败: {str(e)}")

            # 返回按钮
            if st.button("← 返回问答", use_container_width=True):
                st.session_state.show_all_history = False
                st.rerun()

            st.markdown("---")

        # ========== 正常问答模式 ==========
        else:
            st.title("智能问答")

            with st.expander("📖 使用说明", expanded=False):
                st.markdown("""
                1. 先在"文档管理"页面上传文档
                2. 然后在这里提问，系统会基于文档内容回答
                """)

            # 显示历史消息
            for message in st.session_state.messages:
                with st.chat_message(message['role']):
                    st.markdown(message['content'])

                    # 显示来源
                    if message.get('sources'):
                        with st.expander("检索来源"):
                            for source in message['sources']:
                                st.caption(f"{source['source_name']} [相似度: {source['similarity']:.2f}]")

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
                    with st.spinner('思考中...'):
                        try:
                            result = st.session_state.rag_chain.ask(prompt)
                        except Exception as e:
                            st.error(f"❌ 生成回答失败: {str(e)}")
                            st.stop()

                    st.markdown(result['answer'])

                    if result.get('sources'):
                        with st.expander("检索来源"):
                            for source in result['sources']:
                                st.caption(f"{source['source_name']} [相似度: {source['similarity']:.2f}]")

                # 保存到历史（内存）
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': result['answer'],
                    'sources': result.get('sources', []),
                    'metadata': result.get('metadata', {})
                })

                # 保存到数据库
                try:
                    st.session_state.rag_chain.metadata_store.save_chat(
                        question=prompt,
                        answer=result['answer'],
                        sources=result.get('sources', [])
                    )
                except Exception as e:
                    st.warning(f"⚠️ 保存历史记录失败: {str(e)}")

elif page == "文档管理":
    st.title("文档管理")

    st.markdown("---")

    # 上传区域
    st.subheader("上传文档")

    col1, col2 = st.columns(2)

    with col1:
        uploaded_files = st.file_uploader(
            "选择文档",
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

            if st.button("开始处理", type="primary"):
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
    st.subheader("文档列表")

    if not docs:
        st.info("暂无文档")
    else:
        # 添加搜索和过滤功能
        st.markdown("### 搜索和过滤")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            search_query = st.text_input(
                "搜索文档名",
                placeholder="输入关键词...",
                label_visibility="collapsed"
            )

        with col2:
            filter_type = st.selectbox(
                "文档类型",
                ["全部", "pdf", "md", "txt"],
                label_visibility="collapsed"
            )

        with col3:
            filter_status = st.selectbox(
                "状态",
                ["全部", "active", "failed"],
                label_visibility="collapsed",
                format_func=lambda x: {"全部": "全部", "active": "活跃", "failed": "失败"}[x]
            )

        with col4:
            sort_by = st.selectbox(
                "排序",
                ["时间", "大小", "名称"],
                label_visibility="collapsed"
            )

        # 应用过滤和排序
        filtered_docs = docs.copy()

        # 搜索过滤
        if search_query:
            filtered_docs = [d for d in filtered_docs if search_query.lower() in d.file_name.lower()]

        # 类型过滤
        if filter_type != "全部":
            filtered_docs = [d for d in filtered_docs if d.file_type == filter_type]

        # 状态过滤
        if filter_status != "全部":
            filtered_docs = [d for d in filtered_docs if d.status.value == filter_status]

        # 排序
        if sort_by == "大小":
            filtered_docs = sorted(filtered_docs, key=lambda x: x.file_size, reverse=True)
        elif sort_by == "名称":
            filtered_docs = sorted(filtered_docs, key=lambda x: x.file_name)
        else:  # 时间（默认就是按时间倒序）
            pass

        # 显示过滤结果
        if filtered_docs:
            st.caption(f"找到 {len(filtered_docs)} 个文档（共 {len(docs)} 个）")
        else:
            st.warning(f"没有找到匹配的文档（共 {len(docs)} 个）")

        st.markdown("---")

        # 按状态分组显示
        active_docs = [d for d in filtered_docs if d.status.value == 'active']
        indexing_docs = [d for d in filtered_docs if d.status.value == 'indexing']
        failed_docs = [d for d in filtered_docs if d.status.value == 'failed']

        if active_docs:
            st.markdown("### 活跃文档")
            for doc in active_docs:
                with st.expander(f"{doc.file_name}"):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("类型", doc.file_type)
                    col2.metric("大小", f"{doc.file_size / 1024:.1f} KB")
                    col3.metric("块数", doc.chunk_count)
                    col4.metric("状态", doc.status.value)

                    if st.button(f"删除", key=f"delete_{doc.source_id}"):
                        result = st.session_state.rag_chain.delete_document(doc.source_id)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()

        if indexing_docs:
            st.markdown("### 处理中")
            for doc in indexing_docs:
                st.caption(f"{doc.file_name} - 正在处理...")

        if failed_docs:
            st.markdown("### 失败文档")
            for doc in failed_docs:
                with st.expander(f"{doc.file_name}"):
                    st.write(f"**错误信息:** {doc.error_message}")
                    st.caption(f"Source ID: {doc.source_id}")

elif page == "调试":
    st.title("调试面板")

    st.markdown("""
    这里会显示系统的调试信息，包括：
    - 日志输出
    - 统计信息
    - 配置参数
    """)

    st.markdown("---")

    # 系统配置
    st.subheader("系统配置")

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
    st.subheader("统计信息")

    st.json({
        "total_documents": len(docs),
        "active_documents": len(active_docs),
        "total_vectors": vector_stats['total_count'],
        "ollama_connected": st.session_state.get('ollama_connected', False)
    })

    st.markdown("---")

    # 日志查看
    st.subheader("日志")

    log_file = settings.log_file
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.readlines()
            # 显示最后 20 行
            for line in logs[-20:]:
                st.text(line)
    else:
        st.info(f"日志文件不存在: {log_file}")
