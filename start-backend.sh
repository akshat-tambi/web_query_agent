#!/bin/bash

# Development startup script for backend only

echo "🔧 Starting Ripplica Backend Development Server..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers if not already installed
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo "Installing Playwright browsers..."
    playwright install
fi

# Start server
echo "🚀 Starting backend server on http://localhost:8000"
echo "📚 API Documentation available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

python run.py
