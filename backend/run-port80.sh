#!/bin/bash

# SMM Panel Backend - Run on Port 80
# Script để chạy backend trên port 80 cho subdomain

echo "🚀 Starting SMM Panel Backend on port 80..."

# Kill any existing process on port 80
echo "🔄 Stopping existing processes on port 80..."
sudo fuser -k 80/tcp 2>/dev/null || true

# Start backend on port 80
echo "▶️ Starting backend..."
cd /home/homemmo/smm-panel-backend
sudo python3 ultra_simple_backend.py --port 80 &

# Wait for startup
sleep 3

# Test API
echo "🧪 Testing API..."
curl -s http://localhost/health || echo "❌ Health check failed"
curl -s http://localhost/api/services | head -5 || echo "❌ Services endpoint failed"

echo ""
echo "🎉 SMM Panel Backend is running on port 80!"
echo ""
echo "📋 Available endpoints:"
echo "   API: https://social.homemmo.store/api/"
echo "   Health: https://social.homemmo.store/health"
echo "   Docs: https://social.homemmo.store/docs"
echo ""
echo "🔧 Management commands:"
echo "   Stop: sudo fuser -k 80/tcp"
echo "   Restart: ./run-port80.sh"
