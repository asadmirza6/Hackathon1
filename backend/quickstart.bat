@echo off
REM Quick-start script for RAG Chatbot Backend (Windows)

echo 🚀 RAG Chatbot Backend - Quick Start Setup (Windows)
echo ====================================================

REM Check Python
echo ✓ Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo   Python version: %PYTHON_VERSION%

REM Create virtual environment
echo ✓ Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo   Virtual environment created
) else (
    echo   Virtual environment already exists
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo ✓ Installing dependencies (this may take a few minutes)...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    exit /b 1
)
echo   Dependencies installed

REM Check for .env file
echo ✓ Checking environment configuration...
if not exist ".env" (
    echo   ⚠️  .env file not found. Creating template...
    (
        echo # API Configuration
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
        echo API_DEBUG=true
        echo LOG_LEVEL=info
        echo ENVIRONMENT=development
        echo PYTHONPATH=.
        echo.
        echo # Gemini API (REQUIRED - get from https://aistudio.google.com/app/apikeys^)
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # Qdrant Configuration (REQUIRED^)
        echo QDRANT_URL=http://localhost:6333
        echo QDRANT_API_KEY=your_qdrant_password_here
        echo.
        echo # Postgres Database (REQUIRED^)
        echo DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chatbot
    ) > .env.template
    echo   Created .env.template
    echo   Please copy and update with your values:
    echo     copy .env.template .env
    echo     REM Edit .env with your API keys
    exit /b 1
) else (
    echo   .env file found ✓
)

REM Summary
echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Update .env with your API keys (if not already done^)
echo 2. Start the server:
echo    uvicorn main:app --reload
echo 3. Open browser: http://localhost:8000/docs
echo.
echo For detailed setup, see: LOCAL_SETUP.md
