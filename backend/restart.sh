#!/bin/bash

# Quick restart script for SMM Panel Backend

echo "🔄 Restarting SMM Panel Backend..."

# Kill existing process
pkill -f ultra_simple_backend.py
sleep 2

# Start backend
cd /home/homemmo/smm-panel-backend
python3 ultra_simple_backend.py &

# Wait and test
sleep 3
echo "🧪 Testing backend..."
curl -s http://localhost:8000/health
echo ""
echo "✅ Backend restarted successfully!"
echo "🌐 Admin page: http://localhost:8000/admin"
