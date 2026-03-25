#!/bin/bash
# Streamlit 启动脚本

cd ~/ai-knowledge-base
source venv/bin/activate
streamlit run ui/app.py --server.headless true --server.port 8501
