#!/bin/bash
# 云服务器部署脚本 - 更新AI知识库应用

echo "========================================"
echo "  AI 知识库 - 云服务器部署"
echo "========================================"
echo ""

echo "[1] 停止 PM2 服务..."
pm2 stop ai-kb

echo "[2] 拉取最新代码..."
cd /root/ai-knowledge-base
git pull origin main

echo "[3] 重启 PM2 服务..."
pm2 restart ai-kb

echo ""
echo "✅ 部署完成！"
echo ""
echo "查看状态："
pm2 status

echo ""
echo "查看日志："
pm2 logs ai-kb --lines 20
