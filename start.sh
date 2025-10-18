#!/bin/bash

# Absurdly Visual - Startup Script
# This script starts all components of the application

set -e

echo "🎭 Starting Absurdly Visual..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites met${NC}"
echo ""

# Check if .env files exist
echo "🔧 Checking configuration..."

if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env not found, copying from example...${NC}"
    cp backend/.env.example backend/.env
fi

if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}⚠️  frontend/.env not found, copying from example...${NC}"
    cp frontend/.env.example frontend/.env
fi

echo -e "${GREEN}✅ Configuration ready${NC}"
echo ""

# Ask user what to start
echo "What would you like to start?"
echo "1) Everything (Backend + Frontend + Agents)"
echo "2) Backend only"
echo "3) Frontend only"
echo "4) Agents only"
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting everything..."
        echo ""
        
        # Start backend
        echo "Starting backend..."
        cd backend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            source venv/bin/activate
        fi
        python -m uvicorn app.main:socket_app --reload --port 8000 &
        BACKEND_PID=$!
        cd ..
        
        # Start frontend
        echo "Starting frontend..."
        cd frontend
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        npm start &
        FRONTEND_PID=$!
        cd ..
        
        # Start agents
        echo "Starting Fetch.ai agents..."
        cd fetch-agents
        
        # Coordinator
        cd coordinator_agent
        python agent.py &
        COORD_PID=$!
        cd ..
        
        # Video Agent
        cd video_agent
        python agent.py &
        VIDEO_PID=$!
        cd ..
        
        # AI Player
        cd ai_player_agent
        python agent.py &
        AI_PID=$!
        cd ../..
        
        echo ""
        echo -e "${GREEN}✅ All services started!${NC}"
        echo ""
        echo "📍 Access points:"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend:  http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "Press Ctrl+C to stop all services"
        
        # Wait for Ctrl+C
        trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID $COORD_PID $VIDEO_PID $AI_PID 2>/dev/null; exit" INT
        wait
        ;;
        
    2)
        echo ""
        echo "🚀 Starting backend..."
        cd backend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            source venv/bin/activate
        fi
        python -m uvicorn app.main:socket_app --reload --port 8000
        ;;
        
    3)
        echo ""
        echo "🚀 Starting frontend..."
        cd frontend
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        npm start
        ;;
        
    4)
        echo ""
        echo "🚀 Starting Fetch.ai agents..."
        cd fetch-agents
        
        echo "Starting Coordinator Agent on port 8001..."
        cd coordinator_agent
        python agent.py &
        COORD_PID=$!
        cd ..
        
        echo "Starting Video Agent on port 8002..."
        cd video_agent
        python agent.py &
        VIDEO_PID=$!
        cd ..
        
        echo "Starting AI Player Agent on port 8003..."
        cd ai_player_agent
        python agent.py &
        AI_PID=$!
        cd ..
        
        echo ""
        echo -e "${GREEN}✅ All agents started!${NC}"
        echo ""
        echo "📍 Agent endpoints:"
        echo "   Coordinator: http://localhost:8001"
        echo "   Video Agent: http://localhost:8002"
        echo "   AI Player:   http://localhost:8003"
        echo ""
        echo "Press Ctrl+C to stop all agents"
        
        trap "echo ''; echo 'Stopping agents...'; kill $COORD_PID $VIDEO_PID $AI_PID 2>/dev/null; exit" INT
        wait
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
