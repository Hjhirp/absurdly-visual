#!/bin/bash

# Build Frontend for Production
echo "🏗️  Building frontend for PRODUCTION..."
echo "📍 API: https://your-production-api.com"
echo "📍 WebSocket: wss://your-production-api.com"
echo ""

# Build optimized production bundle
npm run build:prod

echo ""
echo "✅ Production build complete!"
echo "📦 Files are in ./build/"
echo "🚀 Ready to deploy!"
