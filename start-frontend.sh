#!/bin/bash

# Development startup script for frontend only

echo "🎨 Starting Ripplica Frontend Development Server..."

cd frontend

# Install dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start development server
echo "🚀 Starting frontend server on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"

npm run dev
