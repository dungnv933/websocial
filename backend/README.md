# SMM Panel Backend

Backend API cho hệ thống SMM Panel (Social Media Marketing Panel) tích hợp với BUMX API.

## 🚀 Tính năng

- **Authentication**: JWT-based authentication với register/login
- **Services Management**: Lấy danh sách dịch vụ từ BUMX API với Redis caching
- **Order Management**: Tạo và quản lý đơn hàng SMM services
- **Balance Management**: Quản lý số dư và giao dịch của user
- **Promotions**: Hệ thống khuyến mãi và giảm giá
- **Real-time Integration**: Tích hợp real-time với BUMX API

## 🛠 Tech Stack

- **FastAPI** (Python 3.11+) - Web framework
- **PostgreSQL** - Database chính
- **Redis** - Caching và session storage
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Docker & Docker Compose** - Containerization
- **Alembic** - Database migrations

## 📁 Cấu trúc Project

```
smm_panel_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings và environment variables
│   ├── database.py             # PostgreSQL connection
│   ├── dependencies.py         # FastAPI dependencies
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── order.py
│   │   └── transaction.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── order.py
│   │   └── service.py
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── services.py
│   │   ├── orders.py
│   │   ├── balance.py
│   │   └── promotions.py
│   └── utils/                  # Utility modules
│       ├── __init__.py
│       ├── bumx_client.py
│       ├── auth.py
│       └── redis_client.py
├── alembic/                    # Database migrations
├── tests/                      # Test files
├── docker-compose.yml          # Docker services
├── Dockerfile                  # FastAPI container
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Setup trên VPS

```bash
# Clone project
git clone <repository-url>
cd smm_panel_backend

# Cài đặt Docker và Docker Compose
chmod +x setup-docker.sh
./setup-docker.sh

# Logout và login lại để apply docker group
# Hoặc chạy: newgrp docker
```

### 2. Chạy Backend

```bash
# Chạy backend với Docker Compose
chmod +x run-backend.sh
./run-backend.sh

# Hoặc chạy manual:
docker-compose up -d --build
```

### 3. Setup Production với Subdomain

```bash
# Setup production với nginx reverse proxy
chmod +x setup-production.sh
./setup-production.sh

# Chạy production
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3. Chạy Database Migrations

```bash
# Chạy migrations
docker-compose exec backend alembic upgrade head

# Tạo migration mới (nếu cần)
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### 4. Test API

```bash
# Mở Swagger UI
open http://localhost:8000/docs

# Test endpoints
curl http://localhost:8000/api/services
curl http://localhost:8000/health
```

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký user mới
- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Thông tin user hiện tại

### Services
- `GET /api/services` - Lấy danh sách dịch vụ
- `GET /api/services/categories` - Lấy danh sách categories

### Orders
- `POST /api/orders` - Tạo đơn hàng mới
- `GET /api/orders/{order_id}` - Chi tiết đơn hàng
- `GET /api/orders/history` - Lịch sử đơn hàng

### Balance
- `GET /api/balance` - Xem số dư
- `POST /api/balance/deposit` - Nạp tiền
- `GET /api/balance/transactions` - Lịch sử giao dịch

### Promotions
- `GET /api/promotions` - Danh sách khuyến mãi

## 🔧 Environment Variables

```env
# Database
DATABASE_URL=postgresql://smm_user:password123@localhost:5432/smm_panel

# Redis
REDIS_URL=redis://localhost:6379/0

# BUMX API
BUMX_API_URL=https://api-v2.bumx.vn/api/v2
BUMX_API_KEY=your-bumx-api-key

# JWT
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=43200

# App
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🧪 Test Scenarios

### 1. User Registration & Login
```bash
# Register
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 2. Deposit Balance
```bash
# Deposit (sử dụng token từ login)
curl -X POST "http://localhost:8000/api/balance/deposit" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0}'
```

### 3. Create Order
```bash
# Create order
curl -X POST "http://localhost:8000/api/orders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"service_id": 1, "link": "https://example.com", "quantity": 1000}'
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild và start
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Execute commands trong container
docker-compose exec backend bash
docker-compose exec backend alembic upgrade head

# Clean up
docker-compose down -v
```

## 🔍 Development

### Chạy Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL và Redis
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Tạo migration mới
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📊 Monitoring

- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs` (Swagger UI)
- **Logs**: `docker-compose logs -f backend`

## 🔒 Security Features

- JWT-based authentication
- Password hashing với bcrypt
- CORS configuration
- Input validation với Pydantic
- SQL injection protection với SQLAlchemy
- Rate limiting (có thể thêm)

## 🚀 Production Deployment

1. **Environment Setup**:
   - Set `DEBUG=False`
   - Use strong `JWT_SECRET_KEY`
   - Configure production database
   - Set up SSL/TLS

2. **Docker Production**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Database Backup**:
   ```bash
   docker-compose exec postgres pg_dump -U smm_user smm_panel > backup.sql
   ```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

Nếu gặp vấn đề, hãy tạo issue hoặc liên hệ team development.

---

**Happy Coding! 🎉**
