@echo off
chcp 65001 >nul
echo ============================================================
echo Starting Lewis AI System Task Queue Worker...
echo ============================================================
echo Queue: orchestrator
echo Status: Listening...
echo ============================================================
echo.
echo [!] Note: Worker requires Redis service running
echo     If Redis is not running, please start Redis first
echo ============================================================
echo.

python -c "from app.tasks.worker import run_worker; run_worker()"

if errorlevel 1 (
    echo.
    echo [X] Worker startup failed
    echo.
    echo Possible causes:
    echo 1. Redis service not running
    echo 2. Redis connection configuration error
    echo 3. Missing required Python packages
    echo.
    echo Please check:
    echo - Is Redis running: redis-cli ping
    echo - Is REDIS_URL environment variable correctly configured
    echo.
    pause
)


