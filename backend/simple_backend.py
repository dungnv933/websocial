"""
Simple FastAPI Backend for SMM Panel
Compatible with Python 3.6 and existing packages
"""
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
import json
from datetime import datetime
from typing import Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SMM Panel API",
    description="Social Media Marketing Panel Backend API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://social.homemmo.store", "http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            balance REAL DEFAULT 0,
            total_spent REAL DEFAULT 0,
            tier_level INTEGER DEFAULT 1,
            tier_name TEXT DEFAULT 'Cấp 1',
            tier_discount REAL DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by_code TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            rate REAL NOT NULL,
            min_quantity INTEGER DEFAULT 1,
            max_quantity INTEGER DEFAULT 10000,
            provider TEXT DEFAULT 'BUMX',
            provider_service_id TEXT,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            link TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            charge REAL NOT NULL,
            start_count INTEGER,
            remains INTEGER,
            status TEXT DEFAULT 'pending',
            bumx_order_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (service_id) REFERENCES services (id)
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_before REAL NOT NULL,
            balance_after REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create deposits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            method TEXT DEFAULT 'bank_transfer',
            bank_name TEXT DEFAULT 'ACB',
            transaction_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    referral_code: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class OrderCreate(BaseModel):
    service_id: int
    link: str
    quantity: int

# Initialize database
init_db()

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SMM Panel API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SMM Panel Backend", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
async def api_health():
    """API health check"""
    return {"status": "ok", "message": "API is running"}

# Auth endpoints
@app.post("/api/auth/register")
async def register(user: UserCreate):
    """Register new user"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    try:
        # Simple password hash (in production, use proper hashing)
        password_hash = user.password  # TODO: Use proper hashing
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, referral_code)
            VALUES (?, ?, ?, ?)
        ''', (user.username, user.email, password_hash, user.referral_code))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        return {"message": "User registered successfully", "user_id": user_id}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    finally:
        conn.close()

@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Login user"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, balance, total_spent, tier_level, tier_name
        FROM users WHERE username = ? AND password_hash = ?
    ''', (user.username, user.password))
    
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Simple JWT token (in production, use proper JWT)
    token = f"fake-jwt-token-{user_data[0]}"
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_data[0],
            "username": user_data[1],
            "email": user_data[2],
            "balance": user_data[3],
            "total_spent": user_data[4],
            "tier_level": user_data[5],
            "tier_name": user_data[6]
        }
    }

@app.get("/api/auth/me")
async def get_current_user():
    """Get current user info"""
    # TODO: Implement proper JWT validation
    return {"message": "User info endpoint"}

# Services endpoints
@app.get("/api/services")
async def get_services():
    """Get all services"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM services WHERE status = "active"')
    services = cursor.fetchall()
    conn.close()
    
    return {
        "services": [
            {
                "id": s[0],
                "name": s[1],
                "category": s[2],
                "rate": s[3],
                "min_quantity": s[4],
                "max_quantity": s[5],
                "provider": s[6],
                "description": s[8]
            }
            for s in services
        ]
    }

# Admin endpoints
@app.get("/api/admin/stats")
async def get_admin_stats():
    """Get admin dashboard stats"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Get user count
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # Get order count
    cursor.execute('SELECT COUNT(*) FROM orders')
    total_orders = cursor.fetchone()[0]
    
    # Get total revenue
    cursor.execute('SELECT SUM(charge) FROM orders WHERE status = "completed"')
    total_revenue = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "stats": {
            "totalUsers": total_users,
            "totalOrders": total_orders,
            "totalRevenue": total_revenue,
            "apiStatus": "Online"
        },
        "recentOrders": [],
        "recentUsers": []
    }

@app.get("/api/admin/users")
async def get_admin_users():
    """Get users for admin"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, balance, total_spent, status, created_at FROM users')
    users = cursor.fetchall()
    conn.close()
    
    return {
        "users": [
            {
                "id": u[0],
                "username": u[1],
                "email": u[2],
                "balance": u[3],
                "total_spent": u[4],
                "is_active": u[5] == "active",
                "created_at": u[6]
            }
            for u in users
        ],
        "total": len(users),
        "page": 1,
        "per_page": 20
    }

@app.get("/api/admin/orders")
async def get_admin_orders():
    """Get orders for admin"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT o.id, o.user_id, u.email, s.name, o.charge, o.status, o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN services s ON o.service_id = s.id
        ORDER BY o.created_at DESC
    ''')
    orders = cursor.fetchall()
    conn.close()
    
    return {
        "orders": [
            {
                "id": o[0],
                "user_id": o[1],
                "user_email": o[2],
                "service_name": o[3],
                "price": o[4],
                "status": o[5],
                "created_at": o[6]
            }
            for o in orders
        ],
        "total": len(orders),
        "page": 1,
        "per_page": 20
    }

@app.get("/api/admin/deposits")
async def get_admin_deposits():
    """Get deposits for admin"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM deposits')
    deposits = cursor.fetchall()
    conn.close()
    
    return {
        "deposits": [
            {
                "id": d[0],
                "user_id": d[1],
                "amount": d[2],
                "method": d[3],
                "status": d[6],
                "created_at": d[7]
            }
            for d in deposits
        ],
        "total": len(deposits),
        "page": 1,
        "per_page": 20
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
