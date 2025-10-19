#!/bin/bash

# Start Frontend in Stage Mode
echo "🚀 Starting frontend in STAGE mode..."
echo "📍 API: http://localhost:8000"
echo "📍 WebSocket: ws://localhost:8000"
echo ""

# Start React dev server with stage env
npm run start:stage
