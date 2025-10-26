#!/bin/bash

# SMM Panel Backend - Run Script
# Script để chạy backend với Docker Compose

echo "🚀 Starting SMM Panel Backend..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please run setup-docker.sh first"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please run setup-docker.sh first"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp env.production .env
    echo "⚠️  Please edit .env file with your actual values before continuing"
    echo "   Especially: DATABASE_URL, JWT_SECRET_KEY, BUMX_API_KEY"
    read -p "Press Enter after editing .env file..."
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec backend alembic upgrade head

# Test API endpoints
echo "🧪 Testing API endpoints..."
sleep 5

# Test health endpoint
echo "Testing health endpoint..."
curl -f http://localhost:8000/health || echo "❌ Health check failed"

# Test services endpoint
echo "Testing services endpoint..."
curl -f http://localhost:8000/api/services || echo "❌ Services endpoint failed"

echo ""
echo "🎉 SMM Panel Backend is running!"
echo ""
echo "📋 Available endpoints:"
echo "   Health Check: http://localhost:8000/health"
echo "   API Docs: http://localhost:8000/docs"
echo "   Services: http://localhost:8000/api/services"
echo ""
echo "🔧 Management commands:"
echo "   View logs: docker-compose logs -f backend"
echo "   Stop services: docker-compose down"
echo "   Restart: docker-compose restart backend"
echo ""
echo "🌐 For production with subdomain:"
echo "   1. Update CORS_ORIGINS in .env"
echo "   2. Configure reverse proxy (nginx)"
echo "   3. Set up SSL certificates"
