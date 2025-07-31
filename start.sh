#!/bin/bash

# Ripplica Project Startup Script

echo "🚀 Starting Ripplica Web Query Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is required but not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All dependencies found${NC}"

# Set up backend
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
pip install -r requirements.txt

# Install Playwright browsers
echo -e "${YELLOW}Installing Playwright browsers...${NC}"
playwright install

# Start backend server in background
echo -e "${GREEN}🔧 Starting backend server...${NC}"
python run.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Set up frontend
echo -e "${BLUE}Setting up frontend...${NC}"
cd ../frontend

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Start frontend server
echo -e "${GREEN}🎨 Starting frontend server...${NC}"
npm run dev &
FRONTEND_PID=$!

# Print success message
echo -e "${GREEN}"
echo "🎉 Ripplica is now running!"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo -e "${NC}"

# Function to cleanup processes
cleanup() {
    echo -e "${YELLOW}Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}Services stopped. Goodbye!${NC}"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup INT

# Wait for processes
wait
