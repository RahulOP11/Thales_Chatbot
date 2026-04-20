#!/bin/bash
# Quick Setup Script for Linux/Mac

echo "================================"
echo "Thales Chatbot - Quick Setup"
echo "================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠ Virtual environment not detected!"
    echo "Please run: python3 -m venv venv"
    echo "Then activate: source venv/bin/activate"
    echo ""
    exit 1
fi

echo "✓ Virtual environment detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "✗ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠ IMPORTANT: Edit .env and add your GOOGLE_API_KEY"
    echo "Get free key from: https://makersuite.google.com/app/apikey"
    echo ""
else
    echo "✓ .env file already exists"
fi

echo ""
echo "================================"
echo "Next Steps:"
echo "================================"
echo ""
echo "1. Add your Gemini API key to .env file"
echo "2. Download textbooks: python src/utils/download_textbooks.py"
echo "3. Build vector store: python build_vectorstore.py"
echo "4. Start API server: python main.py"
echo ""
echo "Full documentation: README.md"
echo ""
