# SMM Panel - Deployment Guide

## 📋 Yêu cầu hệ thống

### Server Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Tối thiểu 2GB (khuyến nghị 4GB+)
- **CPU**: 2 cores+
- **Storage**: 20GB+
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Nginx**: 1.18+

### Domain & SSL
- Domain đã trỏ về server
- SSL certificate (Let's Encrypt hoặc Cloudflare)

## 🚀 Deployment Steps

### 1. Chuẩn bị Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx git curl

# Install Redis (for background tasks)
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 2. Setup PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE smmpanel;
CREATE USER smmpanel_user WITH PASSWORD 'your_strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE smmpanel TO smmpanel_user;
\q

# Test connection
psql -U smmpanel_user -d smmpanel -h localhost
```

### 3. Deploy Backend

```bash
# Create app directory
sudo mkdir -p /var/www/smmpanel
sudo chown $USER:$USER /var/www/smmpanel

# Clone or upload code
cd /var/www/smmpanel
# Upload your backend code here

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
# Database
DATABASE_URL=postgresql://smmpanel_user:your_strong_password_here@localhost/smmpanel

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# BUMX API
BUMX_API_URL=https://api.bumx.vn/v2
BUMX_API_KEY=your_bumx_api_key_here

# Sepay
SEPAY_API_URL=https://my.sepay.vn/userapi
SEPAY_API_KEY=your_sepay_api_key_here
SEPAY_ACCOUNT_NUMBER=your_account_number
SEPAY_SECRET=your_sepay_secret

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# CORS
CORS_ORIGINS=["https://homemmo.store","https://www.homemmo.store"]
EOF

# Run database migrations
alembic upgrade head

# Test run
python3 run.py
# Ctrl+C to stop
```

### 4. Setup Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/smmpanel.service
```

Paste this content:

```ini
[Unit]
Description=SMM Panel FastAPI Application
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/smmpanel
Environment="PATH=/var/www/smmpanel/venv/bin"
ExecStart=/var/www/smmpanel/venv/bin/python3 /var/www/smmpanel/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Set permissions
sudo chown -R www-data:www-data /var/www/smmpanel

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable smmpanel
sudo systemctl start smmpanel

# Check status
sudo systemctl status smmpanel

# View logs
sudo journalctl -u smmpanel -f
```

### 5. Setup Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/smmpanel
```

Paste this content:

```nginx
# Backend API
server {
    listen 80;
    server_name api.homemmo.store;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.homemmo.store;

    # SSL Configuration (use Certbot or Cloudflare)
    ssl_certificate /etc/letsencrypt/live/api.homemmo.store/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.homemmo.store/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}

# Frontend
server {
    listen 80;
    server_name homemmo.store www.homemmo.store;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name homemmo.store www.homemmo.store;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/homemmo.store/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/homemmo.store/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /home/homemmo/domains/homemmo.store/public_html/social;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location / {
        try_files $uri $uri/ =404;
    }

    # Admin dashboard
    location /admin {
        try_files $uri $uri/ /admin.html;
    }

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/smmpanel /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 6. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificates
sudo certbot --nginx -d api.homemmo.store
sudo certbot --nginx -d homemmo.store -d www.homemmo.store

# Auto-renewal
sudo certbot renew --dry-run
```

### 7. Setup Firewall

```bash
# Install UFW
sudo apt install -y ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Check status
sudo ufw status
```

### 8. Setup Background Tasks (Celery)

```bash
# Create Celery service
sudo nano /etc/systemd/system/smmpanel-worker.service
```

```ini
[Unit]
Description=SMM Panel Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/smmpanel
Environment="PATH=/var/www/smmpanel/venv/bin"
ExecStart=/var/www/smmpanel/venv/bin/celery -A app.tasks.celery_app worker --loglevel=info --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable smmpanel-worker
sudo systemctl start smmpanel-worker
sudo systemctl status smmpanel-worker
```

## 🔧 Configuration

### Update Frontend API URL

Edit `/home/homemmo/domains/homemmo.store/public_html/social/admin/api-client.js`:

```javascript
const API_CONFIG = {
    baseURL: 'https://api.homemmo.store/api',  // Production URL
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
};
```

### Update CORS Origins

Edit `/var/www/smmpanel/.env`:

```bash
CORS_ORIGINS=["https://homemmo.store","https://www.homemmo.store"]
```

## 📊 Monitoring

### View Logs

```bash
# Backend logs
sudo journalctl -u smmpanel -f

# Celery logs
sudo journalctl -u smmpanel-worker -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Health Checks

```bash
# Backend health
curl https://api.homemmo.store/health

# Database connection
sudo -u postgres psql -d smmpanel -c "SELECT COUNT(*) FROM users;"

# Redis
redis-cli ping
```

## 🔄 Updates & Maintenance

### Update Backend Code

```bash
cd /var/www/smmpanel

# Backup database
sudo -u postgres pg_dump smmpanel > backup_$(date +%Y%m%d).sql

# Pull new code
git pull origin main

# Activate venv
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart services
sudo systemctl restart smmpanel
sudo systemctl restart smmpanel-worker
```

### Database Backup

```bash
# Create backup script
sudo nano /usr/local/bin/backup-smmpanel.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/smmpanel"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump smmpanel | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-smmpanel.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-smmpanel.sh
```

## [object Object]d not starting

```bash
# Check logs
sudo journalctl -u smmpanel -n 50

# Check if port is in use
sudo lsof -i :8000

# Test manually
cd /var/www/smmpanel
source venv/bin/activate
python3 run.py
```

### Database connection issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U smmpanel_user -d smmpanel -h localhost

# Check .env file
cat /var/www/smmpanel/.env | grep DATABASE_URL
```

### Nginx errors

```bash
# Test config
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

## 📈 Performance Optimization

### Enable Gzip Compression

Add to Nginx config:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_services_status ON services(status);

-- Analyze tables
ANALYZE users;
ANALYZE orders;
ANALYZE services;
```

### Redis Caching

```python
# Add to backend for caching services
from redis import Redis
redis_client = Redis(host='localhost', port=6379, db=0)
```

## ✅ Post-Deployment Checklist

- [ ] Backend running on port 8000
- [ ] Database migrations completed
- [ ] Nginx configured and running
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Background tasks running
- [ ] Frontend can connect to backend
- [ ] Admin login works
- [ ] API endpoints responding
- [ ] Logs are accessible
- [ ] Backups configured
- [ ] Monitoring setup

## 🎉 Done!

Your SMM Panel is now deployed and running!

- **Frontend**: https://homemmo.store
- **Admin**: https://homemmo.store/admin.html
- **API**: https://api.homemmo.store
- **API Docs**: https://api.homemmo.store/docs

---

**Need help?** Check logs first, then review this guide step by step.

## 📋 Yêu cầu hệ thống

### Server Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Tối thiểu 2GB (khuyến nghị 4GB+)
- **CPU**: 2 cores+
- **Storage**: 20GB+
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Nginx**: 1.18+

### Domain & SSL
- Domain đã trỏ về server
- SSL certificate (Let's Encrypt hoặc Cloudflare)

## 🚀 Deployment Steps

### 1. Chuẩn bị Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx git curl

# Install Redis (for background tasks)
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 2. Setup PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE smmpanel;
CREATE USER smmpanel_user WITH PASSWORD 'your_strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE smmpanel TO smmpanel_user;
\q

# Test connection
psql -U smmpanel_user -d smmpanel -h localhost
```

### 3. Deploy Backend

```bash
# Create app directory
sudo mkdir -p /var/www/smmpanel
sudo chown $USER:$USER /var/www/smmpanel

# Clone or upload code
cd /var/www/smmpanel
# Upload your backend code here

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
# Database
DATABASE_URL=postgresql://smmpanel_user:your_strong_password_here@localhost/smmpanel

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# BUMX API
BUMX_API_URL=https://api.bumx.vn/v2
BUMX_API_KEY=your_bumx_api_key_here

# Sepay
SEPAY_API_URL=https://my.sepay.vn/userapi
SEPAY_API_KEY=your_sepay_api_key_here
SEPAY_ACCOUNT_NUMBER=your_account_number
SEPAY_SECRET=your_sepay_secret

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# CORS
CORS_ORIGINS=["https://homemmo.store","https://www.homemmo.store"]
EOF

# Run database migrations
alembic upgrade head

# Test run
python3 run.py
# Ctrl+C to stop
```

### 4. Setup Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/smmpanel.service
```

Paste this content:

```ini
[Unit]
Description=SMM Panel FastAPI Application
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/smmpanel
Environment="PATH=/var/www/smmpanel/venv/bin"
ExecStart=/var/www/smmpanel/venv/bin/python3 /var/www/smmpanel/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Set permissions
sudo chown -R www-data:www-data /var/www/smmpanel

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable smmpanel
sudo systemctl start smmpanel

# Check status
sudo systemctl status smmpanel

# View logs
sudo journalctl -u smmpanel -f
```

### 5. Setup Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/smmpanel
```

Paste this content:

```nginx
# Backend API
server {
    listen 80;
    server_name api.homemmo.store;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.homemmo.store;

    # SSL Configuration (use Certbot or Cloudflare)
    ssl_certificate /etc/letsencrypt/live/api.homemmo.store/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.homemmo.store/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}

# Frontend
server {
    listen 80;
    server_name homemmo.store www.homemmo.store;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name homemmo.store www.homemmo.store;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/homemmo.store/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/homemmo.store/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /home/homemmo/domains/homemmo.store/public_html/social;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location / {
        try_files $uri $uri/ =404;
    }

    # Admin dashboard
    location /admin {
        try_files $uri $uri/ /admin.html;
    }

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/smmpanel /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 6. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificates
sudo certbot --nginx -d api.homemmo.store
sudo certbot --nginx -d homemmo.store -d www.homemmo.store

# Auto-renewal
sudo certbot renew --dry-run
```

### 7. Setup Firewall

```bash
# Install UFW
sudo apt install -y ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Check status
sudo ufw status
```

### 8. Setup Background Tasks (Celery)

```bash
# Create Celery service
sudo nano /etc/systemd/system/smmpanel-worker.service
```

```ini
[Unit]
Description=SMM Panel Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/smmpanel
Environment="PATH=/var/www/smmpanel/venv/bin"
ExecStart=/var/www/smmpanel/venv/bin/celery -A app.tasks.celery_app worker --loglevel=info --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable smmpanel-worker
sudo systemctl start smmpanel-worker
sudo systemctl status smmpanel-worker
```

## 🔧 Configuration

### Update Frontend API URL

Edit `/home/homemmo/domains/homemmo.store/public_html/social/admin/api-client.js`:

```javascript
const API_CONFIG = {
    baseURL: 'https://api.homemmo.store/api',  // Production URL
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
};
```

### Update CORS Origins

Edit `/var/www/smmpanel/.env`:

```bash
CORS_ORIGINS=["https://homemmo.store","https://www.homemmo.store"]
```

## 📊 Monitoring

### View Logs

```bash
# Backend logs
sudo journalctl -u smmpanel -f

# Celery logs
sudo journalctl -u smmpanel-worker -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Health Checks

```bash
# Backend health
curl https://api.homemmo.store/health

# Database connection
sudo -u postgres psql -d smmpanel -c "SELECT COUNT(*) FROM users;"

# Redis
redis-cli ping
```

## 🔄 Updates & Maintenance

### Update Backend Code

```bash
cd /var/www/smmpanel

# Backup database
sudo -u postgres pg_dump smmpanel > backup_$(date +%Y%m%d).sql

# Pull new code
git pull origin main

# Activate venv
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart services
sudo systemctl restart smmpanel
sudo systemctl restart smmpanel-worker
```

### Database Backup

```bash
# Create backup script
sudo nano /usr/local/bin/backup-smmpanel.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/smmpanel"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump smmpanel | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-smmpanel.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-smmpanel.sh
```

## [object Object]d not starting

```bash
# Check logs
sudo journalctl -u smmpanel -n 50

# Check if port is in use
sudo lsof -i :8000

# Test manually
cd /var/www/smmpanel
source venv/bin/activate
python3 run.py
```

### Database connection issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U smmpanel_user -d smmpanel -h localhost

# Check .env file
cat /var/www/smmpanel/.env | grep DATABASE_URL
```

### Nginx errors

```bash
# Test config
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

## 📈 Performance Optimization

### Enable Gzip Compression

Add to Nginx config:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_services_status ON services(status);

-- Analyze tables
ANALYZE users;
ANALYZE orders;
ANALYZE services;
```

### Redis Caching

```python
# Add to backend for caching services
from redis import Redis
redis_client = Redis(host='localhost', port=6379, db=0)
```

## ✅ Post-Deployment Checklist

- [ ] Backend running on port 8000
- [ ] Database migrations completed
- [ ] Nginx configured and running
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Background tasks running
- [ ] Frontend can connect to backend
- [ ] Admin login works
- [ ] API endpoints responding
- [ ] Logs are accessible
- [ ] Backups configured
- [ ] Monitoring setup

## 🎉 Done!

Your SMM Panel is now deployed and running!

- **Frontend**: https://homemmo.store
- **Admin**: https://homemmo.store/admin.html
- **API**: https://api.homemmo.store
- **API Docs**: https://api.homemmo.store/docs

---

**Need help?** Check logs first, then review this guide step by step.




