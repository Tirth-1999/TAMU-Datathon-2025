#!/bin/bash

# Run API Server Script
# TAMU Datathon 2025 - Regulatory Document Classifier

echo "🚀 Starting Regulatory Document Classifier API..."
echo "================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r backend/requirements.txt
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚙️  Please edit .env and add your API keys!"
    echo "   ANTHROPIC_API_KEY=your_key_here"
    echo "   OPENAI_API_KEY=your_key_here (optional)"
    exit 1
fi

# Create necessary directories
mkdir -p uploads temp logs

# Initialize database if not exists
if [ ! -f "regulatory_classifier.db" ]; then
    echo "🗄️  Initializing database..."
    python -c "from backend.database import init_db; init_db()"
fi

# Run the API server
echo "✅ Starting API server on http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "================================================="
python -m uvicorn backend.main:app --reload --port 8000
