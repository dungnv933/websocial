# SMM Panel - Social Media Marketing Panel

Complete social media marketing platform with admin dashboard and order management.

## 📁 Project Structure

```
social/
├── index.html          # Frontend SMM Panel (User Interface)
├── admin.html          # Admin Dashboard
├── app.js              # Frontend JavaScript
├── style.css           # Frontend Styling
├── .htaccess           # Apache Configuration
├── admin.php           # PHP Proxy for Backend API
└── backend/            # Backend API (FastAPI + SQLite)
    ├── ultra_simple_backend.py
    ├── smm_panel.db
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   ├── database.py
    │   ├── models/
    │   ├── schemas/
    │   ├── api/
    │   └── utils/
    └── requirements.txt
```

## 🌐 URLs

- **Frontend:** https://social.homemmo.store/
- **Admin Dashboard:** https://social.homemmo.store/admin
- **API Docs:** https://social.homemmo.store/docs

## 🚀 Features

### Frontend (User)
- ✅ Service catalog with categories (Facebook, TikTok, YouTube, Instagram)
- ✅ Order form with auto-calculation
- ✅ User profile with 3 tabs (Info, Orders, Transactions)
- ✅ Real-time balance display
- ✅ Responsive design
- ✅ Toast notifications

### Admin Dashboard
- ✅ Statistics cards (Users, Orders, Revenue, API Status)
- ✅ Interactive charts (Revenue, Orders by Service)
- ✅ Data tables with search, filter, pagination
- ✅ User management (Ban/Unban, Add Balance)
- ✅ Order management (Status update, Refund)
- ✅ Transaction history
- ✅ Services synchronization from BUMX API
- ✅ System info and error logs

### Backend API
- ✅ FastAPI with SQLite database
- ✅ BUMX API integration (Services, Orders, Balance)
- ✅ Admin endpoints (Stats, Users, Orders, Transactions)
- ✅ CORS enabled for frontend
- ✅ Error handling and logging

## 📋 Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Bootstrap 4.6.2
- Font Awesome Icons
- jQuery

**Backend:**
- Python 3.6+
- FastAPI
- SQLite
- httpx for API calls
- JWT authentication (disabled in simplified version)

**Infrastructure:**
- LiteSpeed Web Server
- PHP Proxy (admin.php)
- Apache .htaccess routing

## 🔧 Setup

### Requirements
- Python 3.6+
- Git
- Web server (LiteSpeed/Apache)

### Installation

1. **Clone repository:**
```bash
git clone git@github.com:dungnv933/websocial.git
cd websocial
```

2. **Setup Backend:**
```bash
cd backend
pip3 install -r requirements.txt

# Start backend
python3 ultra_simple_backend.py
```

3. **Deploy Frontend:**
- Copy files to web server
- Configure .htaccess for routing
- Update app.js API endpoint if needed

## 📝 Configuration

### Backend Configuration
Edit `backend/.env`:
```
BUMX_API_URL=https://api-v2.bumx.vn/api/v2
BUMX_API_KEY=your-api-key
CORS_ORIGINS=https://social.homemmo.store
```

### Frontend Configuration
Edit `app.js`:
```javascript
const API_CONFIG = {
    baseURL: 'https://social.homemmo.store/api',
    timeout: 10000
};
```

## 🧪 Testing

### Test Frontend
```bash
curl https://social.homemmo.store/
```

### Test Admin Dashboard
```bash
curl https://social.homemmo.store/admin
```

### Test Backend API
```bash
curl https://social.homemmo.store/api/admin/stats
curl https://social.homemmo.store/api/services
```

## 🔄 Deployment

### Manual Deployment
```bash
# Pull latest changes
git pull origin master

# Restart backend
cd backend
python3 ultra_simple_backend.py &
```

### Automated Deployment
See `backend/deploy-vps.sh` for VPS deployment script.

## 📞 Support

- Email: dungnv933@gmail.com
- GitHub: https://github.com/dungnv933/websocial

## 📄 License

Private - All rights reserved

