@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

echo ========================================
echo   启动 Streamlit 前端界面
echo ========================================
echo.

REM 检查虚拟环境是否存在
if exist ".venv\Scripts\activate.bat" (
    echo [1/3] 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境 (.venv)
    echo 将尝试使用系统 Python...
    echo.
)

echo [2/3] 检查依赖...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo 错误: 未安装 streamlit
    echo 请运行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [3/3] 启动界面...
echo.
echo 界面地址: http://localhost:8501
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

streamlit run ui/app.py

if errorlevel 1 (
    echo.
    echo 错误: 界面启动失败
    pause
)

