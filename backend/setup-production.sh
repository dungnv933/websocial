#!/bin/bash

# SMM Panel Backend - Production Setup Script
# Script để setup production với nginx reverse proxy

echo "🚀 Setting up SMM Panel Backend for Production..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root"
    exit 1
fi

# Create SSL directory
echo "📁 Creating SSL directory..."
mkdir -p ssl

# Create nginx configuration
echo "⚙️ Creating nginx configuration..."
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name smm-panel.yourdomain.com admin.smm-panel.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # Main API server
    server {
        listen 443 ssl http2;
        server_name smm-panel.yourdomain.com;

        # SSL configuration (self-signed for testing)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers off;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers
            add_header Access-Control-Allow-Origin "https://admin.smm-panel.yourdomain.com" always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
            add_header Access-Control-Allow-Credentials true always;
            
            # Handle preflight requests
            if ($request_method = 'OPTIONS') {
                add_header Access-Control-Allow-Origin "https://admin.smm-panel.yourdomain.com";
                add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
                add_header Access-Control-Allow-Headers "Authorization, Content-Type";
                add_header Access-Control-Allow-Credentials true;
                add_header Content-Length 0;
                add_header Content-Type text/plain;
                return 204;
            }
        }

        # Health check
        location /health {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API documentation
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Root redirect to docs
        location / {
            return 301 https://$server_name/docs;
        }
    }

    # Admin panel server
    server {
        listen 443 ssl http2;
        server_name admin.smm-panel.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers off;

        # Serve static files for admin panel
        location / {
            root /var/www/admin;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # Proxy API calls to backend
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# Generate self-signed SSL certificate
echo "🔐 Generating self-signed SSL certificate..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=VN/ST=HCM/L=HoChiMinh/O=SMMPanel/OU=IT/CN=smm-panel.yourdomain.com"

# Update docker-compose.prod.yml
echo "🐳 Updating production docker-compose..."
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: smmpanel_db
    environment:
      POSTGRES_USER: smmpanel_user
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: smmpanel_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U smmpanel_user -d smmpanel_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - smm_network

  redis:
    image: redis:7-alpine
    container_name: smmpanel_redis
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - smm_network

  backend:
    build: .
    container_name: smmpanel_backend
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    env_file:
      - env.production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - smm_network

  nginx:
    image: nginx:alpine
    container_name: smmpanel_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - smm_network

volumes:
  postgres_data:
  redis_data:

networks:
  smm_network:
    driver: bridge
EOF

echo ""
echo "🎉 Production setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update domain names in nginx.conf"
echo "2. Get real SSL certificates (Let's Encrypt)"
echo "3. Update CORS_ORIGINS in env.production"
echo "4. Run: docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "🔧 SSL Certificate:"
echo "   Self-signed certificate generated in ssl/ directory"
echo "   For production, replace with real certificates"
echo ""
echo "🌐 Domain Configuration:"
echo "   Update nginx.conf with your actual domain names"
echo "   Point DNS records to this server's IP"
