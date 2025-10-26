#!/bin/bash

# SMM Panel Backend - Docker Setup Script
# Script để cài đặt Docker và Docker Compose trên VPS

echo "🚀 Installing Docker and Docker Compose for SMM Panel Backend..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
echo "🔑 Adding Docker's official GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "📋 Adding Docker repository..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
echo "🐳 Installing Docker..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
echo "👤 Adding user to docker group..."
sudo usermod -aG docker $USER

# Install Docker Compose standalone (backup)
echo "🔧 Installing Docker Compose standalone..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Start Docker service
echo "▶️ Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
echo "✅ Verifying installation..."
docker --version
docker-compose --version

echo ""
echo "🎉 Docker and Docker Compose installed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Logout and login again to apply docker group changes"
echo "2. Or run: newgrp docker"
echo "3. Then run: docker-compose up -d --build"
echo ""
echo "🔧 If you get permission errors, run:"
echo "sudo chmod 666 /var/run/docker.sock"
