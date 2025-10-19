#!/bin/bash

# Run in Production Environment
echo "🚀 Starting server in PRODUCTION mode..."

# Load production environment
export $(cat .env.prod | grep -v '^#' | xargs)

# Run the server with Socket.IO support (no reload in production)
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000
