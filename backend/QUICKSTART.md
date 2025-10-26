# SMM Panel - Quick Start Guide

## 🚀 Chạy nhanh trong 5 phút

### 1. Setup Database (1 phút)

```bash
# Tạo database
createdb smmpanel

# Hoặc với PostgreSQL
sudo -u postgres psql
CREATE DATABASE smmpanel;
\q
```

### 2. Setup Backend (2 phút)

```bash
cd /home/homemmo/websocial/backend

# Install dependencies
pip3 install -r requirements.txt

# Tạo file .env
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost/smmpanel
SECRET_KEY=your-secret-key-change-this-in-production
BUMX_API_KEY=your_bumx_api_key
SEPAY_API_KEY=your_sepay_api_key
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
EOF

# Run migrations
alembic upgrade head

# Start backend
python3 run.py
```

Backend chạy tại: **http://localhost:8000**

### 3. Setup Frontend (1 phút)

```bash
# Mở file api-client.js
nano /home/homemmo/domains/homemmo.store/public_html/social/admin/api-client.js

# Thay đổi baseURL thành:
const API_CONFIG = {
    baseURL: 'http://localhost:8000/api',
    ...
};
```

### 4. Tạo Admin User (30 giây)

```bash
# Mở Python shell
cd /home/homemmo/websocial/backend
python3

# Trong Python shell:
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

db = SessionLocal()

# Tạo admin user
admin = User(
    username="admin",
    email="admin@homemmo.store",
    password_hash=get_password_hash("admin123"),
    balance=0,
    tier_level=4,
    tier_name="VIP",
    tier_discount=15.0,
    referral_code="ADMIN001",
    status="active"
)

db.add(admin)
db.commit()
print("Admin user created!")
exit()
```

### 5. Login & Test (30 giây)

1. Mở trình duyệt: **http://homemmo.store/social/admin/login.html**
2. Login với:
   - Username: `admin`
   - Password: `admin123`
3. Xem dashboard!

## 📝 Thông tin quan trọng

### Default Admin Credentials
```
Username: admin
Password: admin123
```
⚠️ **ĐỔI MẬT KHẨU NGAY SAU KHI LOGIN!**

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Login |
| `/api/auth/register` | POST | Register |
| `/api/services` | GET | Get services |
| `/api/orders` | POST | Create order |
| `/api/user/balance` | GET | Get balance |
| `/api/admin/users` | GET | Get all users (admin) |

### Port Usage

- **Backend**: 8000
- **Frontend**: 80/443 (Nginx)
- **PostgreSQL**: 5432
- **Redis**: 6379

## [object Object]d không chạy?

```bash
# Check Python version
python3 --version  # Cần >= 3.8

# Check dependencies
pip3 list | grep fastapi

# Check database
psql -U postgres -d smmpanel -c "SELECT 1;"
```

### Frontend không kết nối?

```bash
# 1. Check backend đang chạy
curl http://localhost:8000/health

# 2. Check CORS trong .env
cat .env | grep CORS_ORIGINS

# 3. Check browser console (F12)
```

### Database errors?

```bash
# Reset database
dropdb smmpanel
createdb smmpanel
cd /home/homemmo/websocial/backend
alembic upgrade head
```

## 📚 Next Steps

1. **Đọc INTEGRATION_GUIDE.md** - Hiểu cách tích hợp
2. **Đọc DEPLOYMENT.md** - Deploy lên production
3. **Đọc API docs** - http://localhost:8000/docs
4. **Customize** - Thay đổi theo nhu cầu

## 🎯 Testing Checklist

- [ ] Backend chạy tại http://localhost:8000
- [ ] API docs accessible tại /docs
- [ ] Database có tables (users, orders, services, etc.)
- [ ] Admin user đã tạo
- [ ] Login page hoạt động
- [ ] Dashboard load được data
- [ ] Có thể tạo user mới
- [ ] Có thể xem orders
- [ ] Có thể xem services

## 💡 Tips

### Development Mode

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### View Logs

```bash
# Backend logs
tail -f backend.log

# Database queries
# Add to .env:
DATABASE_ECHO=true
```

### Test API with curl

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get services
curl http://localhost:8000/api/services

# Get user info (with token)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🆘 Need Help?

1. Check logs: `tail -f backend.log`
2. Check browser console (F12)
3. Read error messages carefully
4. Check INTEGRATION_GUIDE.md
5. Check DEPLOYMENT.md

## ✅ Success!

Nếu mọi thứ hoạt động:
- ✅ Backend running
- ✅ Database connected
- ✅ Admin login works
- ✅ Dashboard loads

**Bạn đã sẵn sàng![object Object]

---

**Time to complete**: ~5 minutes
**Difficulty**: Easy
**Prerequisites**: Python 3.8+, PostgreSQL

Happy coding! 🚀


