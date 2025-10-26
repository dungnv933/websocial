# SMM Panel - Backend & Frontend Integration Guide

## 🎯 Tổng quan

Đã tích hợp thành công **FastAPI Backend** với **Admin Dashboard Frontend** cho hệ thống SMM Panel.

## 📁 Cấu trúc dự án

```
/home/homemmo/
├── websocial/backend/              # FastAPI Backend (MỚI)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── api/                    # API endpoints
│   │   ├── utils/                  # Utilities
│   │   └── tasks/                  # Background tasks
│   ├── requirements.txt
│   ├── run.py
│   └── README.md
│
└── domains/homemmo.store/public_html/social/
    ├── admin.html                  # Admin Dashboard
    ├── admin/
    │   ├── app.js                  # Frontend logic (ĐÃ CẬP NHẬT)
    │   └── api-client.js           # API Client (MỚI)
    └── index.html                  # User[object Object]Những gì đã tích hợp

### 1. Backend API (FastAPI)

✅ **Database Models**
- User (với tier system & referral)
- Service
- Order
- Transaction
- Deposit

✅ **API Endpoints**
- `/api/auth/*` - Authentication
- `/api/user/*` - User operations
- `/api/services/*` - Services
- `/api/orders/*` - Orders
- `/api/payment/*` - Payments
- `/api/admin/*` - Admin operations

✅ **Business Logic**
- Tier system (4 levels: Cấp 1, Cấp 2, Cấp 3, VIP)
- Referral system (5% commission)
- BUMX API integration
- Sepay webhook handler
- Telegram notifications

### 2. Frontend Integration

✅ **API Client** (`admin/api-client.js`)
- Authentication API
- Users API
- Orders API
- Services API
- Deposits API
- Dashboard API

✅ **Admin Dashboard** (`app.js` - Đã cập nhật)
- ✅ Dashboard: Load stats từ API
- ✅ Users: CRUD operations với API
- ✅ Orders: Load và filter từ API
- ✅ Services: Load từ API
- ✅ Payments: Load deposits từ API
- ⏳ API Providers: Placeholder
- ⏳ Promotions: Placeholder
- ⏳ Support: Placeholder

## 🚀 Cách chạy

### Backend (FastAPI)

```bash
# 1. Cài đặt dependencies
cd /home/homemmo/websocial/backend
pip3 install -r requirements.txt

# 2. Tạo file .env
cp env.example .env
# Chỉnh sửa .env với thông tin database và API keys

# 3. Setup database
createdb smmpanel
alembic upgrade head

# 4. Chạy backend
python3 run.py
# Backend sẽ chạy tại: http://localhost:8000
```

### Frontend (Admin Dashboard)

```bash
# 1. Cập nhật API URL trong api-client.js
# Mở file: /home/homemmo/domains/homemmo.store/public_html/social/admin/api-client.js
# Thay đổi baseURL thành URL backend của bạn

const API_CONFIG = {
    baseURL: 'http://your-backend-url:8000/api',  # Thay đổi URL này
    timeout: 30000,
    ...
};

# 2. Truy cập Admin Dashboard
# http://homemmo.store/social/admin.html
```

## 🔑 Authentication Flow

1. **Login** (Cần tạo trang login)
   - User nhập username/password
   - Call API: `POST /api/auth/login`
   - Nhận JWT token
   - Lưu token vào localStorage
   - Redirect đến admin.html

2. **Protected Routes**
   - Mỗi request gửi token trong header: `Authorization: Bearer {token}`
   - Backend verify token
   - Nếu invalid → 401 → Redirect về login

3. **Logout**
   - Xóa token từ localStorage
   - Redirect về login page

## 📝 Các chức năng đã tích hợp

### Dashboard
- ✅ Load statistics từ API
- ✅ Display recent orders
- ✅ Display recent users
- ✅ Charts (sử dụng data từ API)

### Users Management
- ✅ Load users list từ API
- ✅ Search & filter users
- ✅ Add new user
- ✅ Ban/Unban user
- ⏳ Edit user (chưa implement)
- ⏳ Update balance (chưa implement)

### Orders Management
- ✅ Load orders từ API
- ⏳ Filter orders (cần thêm vào app.js)
- ⏳ View order details
- ⏳ Update order status

### Services Management
- ✅ Load services từ API
- ⏳ Add service (cần tích hợp API)
- ⏳ Edit service
- ⏳ Toggle service status

### Payments
- ✅ Load deposits từ API
- ⏳[object Object] làm tiếp

### 1. Tạo Login Page
```html
<!-- /home/homemmo/domains/homemmo.store/public_html/social/admin/login.html -->
```

### 2. Hoàn thiện các chức năng còn thiếu
- [ ] Edit user
- [ ] Update user balance
- [ ] Filter orders
- [ ] View order details
- [ ] Update order status
- [ ] Add/Edit service
- [ ] Approve deposit
- [ ] API Providers management
- [ ] Promotions management
- [ ] Support tickets

### 3. Cập nhật API Client
Thêm các method còn thiếu vào `api-client.js`:
- Update user balance
- Filter orders với search term
- Approve deposit
- Etc.

### 4. Error Handling
- Hiển thị lỗi chi tiết hơn
- Retry logic cho failed requests
- Loading states

### 5. User Frontend
Tích hợp user-facing frontend với backend API:
- User registration
- User login
- Service browsing
- Order placement
- Balance management

## 🐛 Debugging

### Backend không chạy
```bash
# Check Python version
python3 --version  # Cần >= 3.6

# Check dependencies
pip3 list | grep fastapi

# Check database connection
psql -U postgres -d smmpanel -c "SELECT 1;"

# View logs
tail -f backend.log
```

### Frontend không kết nối được Backend
```bash
# 1. Check CORS settings trong backend
# File: app/main.py
# Đảm bảo frontend URL có trong cors_origins

# 2. Check API URL trong api-client.js
# Đảm bảo baseURL đúng

# 3. Check browser console
# F12 → Console → Xem errors
```

### Authentication issues
```bash
# 1. Check token trong localStorage
localStorage.getItem('admin_token')

# 2. Test API với curl
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/auth/me

# 3. Check token expiration
# Default: 30 minutes
```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    balance FLOAT DEFAULT 0,
    total_spent FLOAT DEFAULT 0,
    tier_level INTEGER DEFAULT 1,
    tier_name VARCHAR(20) DEFAULT 'Cấp 1',
    tier_discount FLOAT DEFAULT 0,
    referral_code VARCHAR(20) UNIQUE NOT NULL,
    referred_by_code VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Orders Table
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    service_id INTEGER REFERENCES services(id),
    link VARCHAR(500) NOT NULL,
    quantity INTEGER NOT NULL,
    charge FLOAT NOT NULL,
    start_count INTEGER,
    remains INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    bumx_order_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

## 🔐 Security Notes

1. **JWT Secret Key**
   - Đổi SECRET_KEY trong .env
   - Sử dụng key mạnh, random

2. **Database Credentials**
   - Không commit .env vào git
   - Sử dụng strong password

3. **CORS**
   - Chỉ allow trusted domains
   - Không dùng wildcard (*) trong production

4. **API Keys**
   - Bảo mật BUMX_API_KEY
   - Bảo mật SEPAY_SECRET
   - Không expose[object Object]

Nếu gặp vấn đề:
1. Check logs: `tail -f backend.log`
2. Check browser console (F12)
3. Test API với Postman/curl
4. Check database connection

## 🎉 Next Steps

1. **Tạo Login Page** cho admin
2. **Test toàn bộ flow** từ login → CRUD operations
3. **Deploy backend** lên server
4. **Cập nhật frontend URL** để trỏ đến backend production
5. **Setup SSL** cho backend API
6. **Monitor & optimize** performance

---

**Status**: Backend hoàn chỉnh ✅ | Frontend tích hợp cơ bản ✅ | Cần hoàn thiện UI/UX ⏳

**Version**: 1.0.0
**Last Updated**: 2025-10-26

