@echo off
echo 🎯 Starting Integrated News Analysis Services...
echo ================================================

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Start Python Bias Detection API (FastAPI)
echo 🚀 Starting Bias Detection API...
start "Bias Detection API" cmd /k "cd /d "%SCRIPT_DIR%python_api" && python main.py"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Python Summarization API (Flask)
echo 🚀 Starting Summarization API...
start "Summarization API" cmd /k "cd /d "%SCRIPT_DIR%python_api" && python summarization.py"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Node.js Backend
echo 🚀 Starting Node.js Backend...
start "Node.js Backend" cmd /k "cd /d "%SCRIPT_DIR%backend" && npm start"

REM Wait a moment
timeout /t 3 /nobreak >nul

echo.
echo ================================================
echo 🎉 All services started!
echo.
echo 📋 Service URLs:
echo    • Bias Detection API: http://localhost:8000
echo    • Summarization API:  http://localhost:5000
echo    • Integrated Backend: http://localhost:3000
echo.
echo 🔗 API Endpoints:
echo    • GET  http://localhost:3000/api/news
echo    • POST http://localhost:3000/api/article/summarize
echo    • POST http://localhost:3000/api/article/bias-analysis
echo    • POST http://localhost:3000/api/article/complete-analysis
echo.
echo ⏹️  Close the command windows to stop services
echo ================================================
echo.
pause 