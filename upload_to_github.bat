@echo off
chcp 65001 >nul
echo ============================================================
echo   Uploading to GitHub
echo ============================================================
echo.

REM 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo [X] Git not installed
    echo Please install Git first: https://git-scm.com/
    pause
    exit /b 1
)

echo [1/6] Checking Git status...
git status

echo.
echo [2/6] Adding all changes...
git add .

echo.
echo [3/6] Committing changes...
git commit -m "Update: Refactor project, improve Writer agent, add screenshots and comprehensive README"

echo.
echo [4/6] Setting remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/Lewis121025/Lewis-first-project.git

echo.
echo [5/6] Pushing to GitHub (main branch)...
git branch -M main
git push -f origin main

echo.
echo [6/6] Done!
echo.
echo ============================================================
echo   Successfully uploaded to GitHub!
echo   Repository: https://github.com/Lewis121025/Lewis-first-project
echo ============================================================
echo.

pause

