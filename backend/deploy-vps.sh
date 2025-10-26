#!/bin/bash

# SMM Panel Backend - Deploy Script
# Script để deploy backend lên VPS DirectAdmin

echo "🚀 Deploying SMM Panel Backend to VPS..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Create deployment directory
echo "📁 Creating deployment directory..."
mkdir -p /home/homemmo/smm-panel-backend
cd /home/homemmo/smm-panel-backend

# Copy project files
echo "📋 Copying project files..."
cp -r "/home/homemmo/web app buff social"/* .

# Set proper permissions
echo "🔐 Setting permissions..."
chmod +x *.sh
chmod 644 *.yml *.conf *.ini *.txt *.md

# Create .env file for production
echo "⚙️ Creating production .env file..."
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://smmpanel_user:your_secure_password@db:5432/smmpanel_db

# Redis
REDIS_URL=redis://redis:6379/0

# BUMX API
BUMX_API_URL=https://api-v2.bumx.vn/api/v2
BUMX_API_KEY=4b45e706-ec05-45d2-bfb5-2efa54e4d84d

# JWT
JWT_SECRET_KEY=thay-bang-random-string-dai-phuc-tap-an-toan-2024-smm-panel-backend
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=43200

# App
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://social.homemmo.store,https://app.homemmo.store,https://api.homemmo.store

# Logging
LOG_LEVEL=INFO
EOF

# Generate SSL certificate
echo "🔐 Generating SSL certificate..."
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=VN/ST=HCM/L=HoChiMinh/O=SMMPanel/OU=IT/CN=social.homemmo.store"

# Update nginx config for homemmo.store
echo "⚙️ Updating nginx configuration..."
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
        server_name social.homemmo.store;
        return 301 https://$server_name$request_uri;
    }

    # Main API server
    server {
        listen 443 ssl http2;
        server_name social.homemmo.store;

        # SSL configuration
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
            add_header Access-Control-Allow-Origin "https://app.homemmo.store" always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
            add_header Access-Control-Allow-Credentials true always;
            
            # Handle preflight requests
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
}
EOF

# Create production docker-compose
echo "🐳 Creating production docker-compose..."
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
      - .env
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

# Install Docker if not installed
echo "🐳 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Test API
echo "🧪 Testing API..."
sleep 10
curl -f http://localhost/health || echo "❌ Health check failed"
curl -f http://localhost/api/services || echo "❌ Services endpoint failed"

echo ""
echo "🎉 SMM Panel Backend deployed successfully!"
echo ""
echo "📋 Available endpoints:"
echo "   API: https://social.homemmo.store/api/"
echo "   Health: https://social.homemmo.store/health"
echo "   Docs: https://social.homemmo.store/docs"
echo ""
echo "🔧 Management commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop: docker-compose -f docker-compose.prod.yml down"
echo "   Restart: docker-compose -f docker-compose.prod.yml restart"
