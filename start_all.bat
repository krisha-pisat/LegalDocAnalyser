@echo off
echo 🚀 Starting LegalDocAnalyser (Unified System)...

:: Check if venv exists
if not exist venv (
    echo ❌ Virtual environment 'venv' not found in the current directory.
    echo Please make sure you are in the project root and venv is installed.
    pause
    exit /b
)

:: 1. Start Search API (Port 5000)
echo 🔍 Starting Search API on port 5000...
start "Search API (5000)" cmd /k "call venv\Scripts\activate && set PYTHONPATH=. && python -m src.api.app"

:: 2. Start RAG Chat API (Port 8000)
echo 🤖 Starting RAG Chat API on port 8000...
start "RAG API (8000)" cmd /k "call venv\Scripts\activate && set PYTHONPATH=. && python -m src.api.rag_api_1"

:: 3. Start Frontend Server (Port 3000)
:: We use python's built-in http server to avoid CORS issues with file://
echo 🌐 Starting Frontend Server on port 3000...
start "Frontend Server (3000)" cmd /k "cd frontend && python -m http.server 3000"

:: Wait for services to warm up
timeout /t 5 /nobreak > nul

:: 4. Open the Web App
echo 🚀 Launching Browser...
start http://localhost:3000/index.html

echo.
echo ✅ System is now running! 
echo ⚠️  KEEP ALL THREE terminal windows open while using the app.
echo.
pause
