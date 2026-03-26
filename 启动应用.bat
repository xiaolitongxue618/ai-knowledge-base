@echo off
echo ========================================
echo   AI 知识库 - Liquid Glass 版本
echo ========================================
echo.
echo [1] 启动 Ollama 服务...
echo [2] 启动 Streamlit 应用
echo.
set /p choice="请选择 (1 或 2): "

if "%choice%"=="1" (
    echo.
    echo 正在启动 Ollama 服务...
    echo 请保持此窗口运行！
    echo.
    ollama serve
) else if "%choice%"=="2" (
    echo.
    echo 正在启动 Streamlit 应用...
    echo.
    cd /d "%~dp0"
    streamlit run ui/app.py --server.port 8502
    pause
) else (
    echo.
    echo 无效选择，请重新运行！
    pause
)
