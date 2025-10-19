#!/bin/bash

# Run in Stage Environment
echo "🚀 Starting server in STAGE mode..."

# Load stage environment
export $(cat .env.stage | grep -v '^#' | xargs)

# Run the server with Socket.IO support
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload
