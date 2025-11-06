@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

echo ========================================
echo   启动 FastAPI 后端服务
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
python -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo 错误: 未安装 uvicorn
    echo 请运行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [3/3] 启动服务器...
echo.
echo 服务器地址: http://127.0.0.1:8002
echo API 文档:   http://127.0.0.1:8002/docs
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

uvicorn app.main:app --reload --host 127.0.0.1 --port 8002

if errorlevel 1 (
    echo.
    echo 错误: 服务器启动失败
    pause
)

