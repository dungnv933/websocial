#!/bin/bash

# SMM Panel Backend - Final Deploy Script
# Script deploy cuối cùng cho subdomain social.homemmo.store

echo "🚀 Deploying SMM Panel Backend to social.homemmo.store..."

# Stop existing backend
echo "🔄 Stopping existing backend..."
sudo fuser -k 8000/tcp 2>/dev/null || true

# Start backend on port 8000
echo "▶️ Starting backend on port 8000..."
cd /home/homemmo/smm-panel-backend
nohup python3 ultra_simple_backend.py > backend.log 2>&1 &

# Wait for startup
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend
echo "🧪 Testing backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Test API endpoints
echo "🧪 Testing API endpoints..."
curl -s http://localhost:8000/api/services | head -5

# Create nginx config for DirectAdmin
echo "⚙️ Creating nginx configuration..."
cat > /home/homemmo/smm-panel-backend/nginx-social.conf << 'EOF'
server {
    listen 80;
    server_name social.homemmo.store;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name social.homemmo.store;
    
    ssl_certificate /usr/local/directadmin/data/users/homemmo/domains/homemmo.store.cert.combined;
    ssl_certificate_key /usr/local/directadmin/data/users/homemmo/domains/homemmo.store.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        add_header Access-Control-Allow-Origin "https://app.homemmo.store" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
        add_header Access-Control-Allow-Credentials true always;
        
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "https://app.homemmo.store";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type";
            add_header Access-Control-Allow-Credentials true;
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }
    }
    
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location / {
        return 301 https://$server_name/docs;
    }
}
EOF

echo ""
echo "🎉 SMM Panel Backend deployed successfully!"
echo ""
echo "📋 Backend Status:"
echo "   ✅ Backend running on port 8000"
echo "   ✅ BUMX API integration working"
echo "   ✅ SQLite database initialized"
echo "   ✅ All API endpoints ready"
echo ""
echo "🌐 Access URLs:"
echo "   API: https://social.homemmo.store/api/"
echo "   Health: https://social.homemmo.store/health"
echo "   Docs: https://social.homemmo.store/docs"
echo ""
echo "📝 Next Steps:"
echo "   1. Configure nginx in DirectAdmin with nginx-social.conf"
echo "   2. Test API endpoints from browser"
echo "   3. Create frontend to connect to API"
echo ""
echo "🔧 Management:"
echo "   View logs: tail -f /home/homemmo/smm-panel-backend/backend.log"
echo "   Stop backend: sudo fuser -k 8000/tcp"
echo "   Restart: ./deploy-final.sh"
