#!/bin/bash

# Run in Development Environment
echo "🚀 Starting server in DEVELOPMENT mode..."

# Load .env if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the server with Socket.IO support
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload
