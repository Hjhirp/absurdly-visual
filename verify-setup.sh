#!/bin/bash

# Setup Verification Script for Absurdly Visual
# Checks if everything is ready to run

set -e

echo "🔍 Verifying Absurdly Visual Setup..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to check command
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to check file
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $1 is missing"
        WARNINGS=$((WARNINGS + 1))
        return 1
    fi
}

# Function to check directory
check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is missing"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

echo "📦 Checking Prerequisites..."
echo ""

# Check Python
if check_command python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "   Version: $PYTHON_VERSION"
fi

# Check Node
if check_command node; then
    NODE_VERSION=$(node --version)
    echo "   Version: $NODE_VERSION"
fi

# Check npm
check_command npm

# Check Docker (optional)
if check_command docker; then
    echo "   Docker is available for containerized deployment"
else
    echo -e "${YELLOW}   Docker is optional but recommended${NC}"
fi

echo ""
echo "📁 Checking Project Structure..."
echo ""

# Check main directories
check_directory "backend"
check_directory "backend/app"
check_directory "backend/data"
check_directory "frontend"
check_directory "frontend/src"
check_directory "fetch-agents"

echo ""
echo "📄 Checking Configuration Files..."
echo ""

# Backend files
check_file "backend/requirements.txt"
check_file "backend/app/main.py"
check_file "backend/app/config.py"
check_file "backend/data/cards.json"

if ! check_file "backend/.env"; then
    echo -e "${BLUE}   Run: cp backend/.env.example backend/.env${NC}"
fi

# Frontend files
check_file "frontend/package.json"
check_file "frontend/src/App.tsx"
check_file "frontend/src/index.tsx"

if ! check_file "frontend/.env"; then
    echo -e "${BLUE}   Run: cp frontend/.env.example frontend/.env${NC}"
fi

# Agent files
check_file "fetch-agents/requirements.txt"
check_file "fetch-agents/coordinator_agent/agent.py"
check_file "fetch-agents/video_agent/agent.py"
check_file "fetch-agents/ai_player_agent/agent.py"

# Docker files
check_file "docker-compose.yml"
check_file "backend/Dockerfile"
check_file "frontend/Dockerfile"

echo ""
echo "🔧 Checking Dependencies..."
echo ""

# Check backend dependencies
if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✓${NC} Backend virtual environment exists"
else
    echo -e "${YELLOW}⚠${NC} Backend virtual environment not found"
    echo -e "${BLUE}   Run: cd backend && python3 -m venv venv${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check frontend dependencies
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Frontend dependencies not installed"
    echo -e "${BLUE}   Run: cd frontend && npm install${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "🎮 Checking Game Data..."
echo ""

# Count cards
if [ -f "backend/data/cards.json" ]; then
    BLACK_CARDS=$(grep -o '"type": "black"' backend/data/cards.json | wc -l)
    WHITE_CARDS=$(grep -o '"type": "white"' backend/data/cards.json | wc -l)
    echo -e "${GREEN}✓${NC} Card database loaded"
    echo "   Black cards: $BLACK_CARDS"
    echo "   White cards: $WHITE_CARDS"
fi

echo ""
echo "🌐 Checking Ports..."
echo ""

# Check if ports are available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Port $1 is already in use"
        WARNINGS=$((WARNINGS + 1))
        return 1
    else
        echo -e "${GREEN}✓${NC} Port $1 is available"
        return 0
    fi
}

check_port 3000  # Frontend
check_port 8000  # Backend
check_port 8001  # Coordinator Agent
check_port 8002  # Video Agent
check_port 8003  # AI Player Agent

echo ""
echo "📋 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! You're ready to go!${NC}"
    echo ""
    echo "🚀 To start the application:"
    echo "   ./start.sh"
    echo ""
    echo "Or manually:"
    echo "   cd backend && python -m uvicorn app.main:socket_app --reload"
    echo "   cd frontend && npm start"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Setup is mostly complete with $WARNINGS warning(s)${NC}"
    echo ""
    echo "You can still run the application, but some features may not work."
    echo ""
    echo "🚀 To start: ./start.sh"
    exit 0
else
    echo -e "${RED}❌ Found $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors above before running the application."
    echo ""
    echo "📚 Check QUICKSTART.md for setup instructions"
    exit 1
fi
