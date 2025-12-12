#!/bin/bash
# Quick-start script for RAG Chatbot Backend (macOS/Linux)

set -e  # Exit on error

echo "🚀 RAG Chatbot Backend - Quick Start Setup"
echo "=========================================="

# Step 1: Check Python
echo "✓ Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "  Python version: $PYTHON_VERSION"

# Step 2: Create virtual environment
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi

# Step 3: Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Step 4: Install dependencies
echo "✓ Installing dependencies (this may take a few minutes)..."
pip install -q -r requirements.txt
echo "  Dependencies installed"

# Step 5: Check for .env file
echo "✓ Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "  ⚠️  .env file not found. Creating template..."
    cat > .env.template << 'EOF'
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
LOG_LEVEL=info
ENVIRONMENT=development
PYTHONPATH=.

# Gemini API (REQUIRED - get from https://aistudio.google.com/app/apikeys)
GEMINI_API_KEY=your_gemini_api_key_here

# Qdrant Configuration (REQUIRED)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_password_here

# Postgres Database (REQUIRED)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chatbot
EOF
    echo "  Created .env.template - please copy and update with your values:"
    echo "    cp .env.template .env"
    echo "    # Edit .env with your API keys"
    exit 1
else
    echo "  .env file found ✓"
fi

# Step 6: Summary
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your API keys (if not already done)"
echo "2. Start the server:"
echo "   uvicorn main:app --reload"
echo "3. Open browser: http://localhost:8000/docs"
echo ""
echo "For detailed setup, see: LOCAL_SETUP.md"
