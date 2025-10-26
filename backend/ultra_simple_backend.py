"""
SMM Panel Backend - Ultra Simple Version
Phiên bản đơn giản nhất để deploy nhanh
"""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pydantic import BaseModel
import httpx
import sqlite3
import json
from datetime import datetime

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cấu hình
BUMX_API_URL = "https://api-v2.bumx.vn/api/v2"
BUMX_API_KEY = "4b45e706-ec05-45d2-bfb5-2efa54e4d84d"

# Tạo FastAPI app
app = FastAPI(
    title="SMM Panel Backend",
    description="Backend API cho SMM Panel - Social Media Marketing Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://social.homemmo.store", "https://app.homemmo.store", "https://api.homemmo.store", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def init_db():
    """Khởi tạo SQLite database"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Tạo bảng users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            total_spent REAL DEFAULT 0.0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tạo bảng orders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            link TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            bumx_order_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Tạo bảng transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_before REAL NOT NULL,
            balance_after REAL NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class OrderCreate(BaseModel):
    service_id: int
    link: str
    quantity: int

class DepositRequest(BaseModel):
    amount: float

# BUMX API client
async def get_bumx_services():
    """Lấy danh sách services từ BUMX API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BUMX_API_URL,
                data={"key": BUMX_API_KEY, "action": "services"},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        logger.error(f"BUMX API error: {e}")
        return []

# API Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SMM Panel Backend", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    return {"message": "SMM Panel Backend API", "docs": "/docs", "admin": "/admin"}

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    try:
        with open("/home/homemmo/smm-admin-simple/admin.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return html_content
    except Exception as e:
        return f"<html><body>Error: Could not load admin page: {str(e)}</body></html>"

@app.post("/api/auth/register")
async def register(user_data: UserCreate):
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Kiểm tra email đã tồn tại
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    
    # Tạo user mới
    cursor.execute(
        "INSERT INTO users (email, password) VALUES (?, ?)",
        (user_data.email, user_data.password)  # Không hash password để đơn giản
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"message": "User created successfully", "user_id": user_id}

@app.post("/api/auth/login")
async def login(user_credentials: UserLogin):
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Tìm user
    cursor.execute("SELECT id, password FROM users WHERE email = ?", (user_credentials.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or user[1] != user_credentials.password:
        raise HTTPException(status_code=401, detail="Email hoặc password không đúng")
    
    # Tạo token đơn giản
    access_token = f"token_{user[0]}_{datetime.utcnow().timestamp()}"
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 43200 * 60,
        "user_id": user[0]
    }

@app.get("/api/services")
async def get_services():
    services = await get_bumx_services()
    return {"services": services, "total": len(services)}

@app.get("/api/balance")
async def get_balance(user_id: int = 1):  # Mock user_id
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"balance": result[0], "currency": "USD"}

@app.post("/api/balance/deposit")
async def deposit_balance(deposit_data: DepositRequest, user_id: int = 1):
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Lấy balance hiện tại
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    old_balance = result[0]
    new_balance = old_balance + deposit_data.amount
    
    # Cập nhật balance
    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
    
    # Tạo transaction
    cursor.execute(
        "INSERT INTO transactions (user_id, type, amount, balance_before, balance_after, description) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, "deposit", deposit_data.amount, old_balance, new_balance, f"Nạp tiền ${deposit_data.amount}")
    )
    
    conn.commit()
    conn.close()
    
    return {"message": f"Nạp tiền thành công ${deposit_data.amount}", "new_balance": new_balance}

@app.post("/api/orders")
async def create_order(order_data: OrderCreate, user_id: int = 1):
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Lấy balance hiện tại
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    balance = result[0]
    price = order_data.quantity * 0.01  # Mock price
    
    if balance < price:
        conn.close()
        raise HTTPException(status_code=400, detail="Số dư không đủ")
    
    # Tạo order
    cursor.execute(
        "INSERT INTO orders (user_id, service_id, service_name, link, quantity, price) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, order_data.service_id, f"Service {order_data.service_id}", order_data.link, order_data.quantity, price)
    )
    order_id = cursor.lastrowid
    
    # Cập nhật balance
    new_balance = balance - price
    cursor.execute("UPDATE users SET balance = ?, total_spent = total_spent + ? WHERE id = ?", 
                  (new_balance, price, user_id))
    
    # Tạo transaction
    cursor.execute(
        "INSERT INTO transactions (user_id, type, amount, balance_before, balance_after, description) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, "order_payment", price, balance, new_balance, f"Thanh toán order {order_id}")
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "Order created successfully", "order_id": order_id, "price": price}

@app.get("/api/orders/history")
async def get_order_history(user_id: int = 1):
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, service_id, service_name, link, quantity, price, status, created_at FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    orders = cursor.fetchall()
    conn.close()
    
    return {
        "orders": [
            {
                "id": order[0],
                "service_id": order[1],
                "service_name": order[2],
                "link": order[3],
                "quantity": order[4],
                "price": order[5],
                "status": order[6],
                "created_at": order[7]
            }
            for order in orders
        ],
        "total": len(orders)
    }

@app.get("/api/promotions")
async def get_promotions():
    return [
        {
            "id": "first_order",
            "name": "Giảm giá đơn hàng đầu tiên",
            "description": "Giảm 10% cho đơn hàng đầu tiên của bạn",
            "discount_percentage": 10,
            "is_active": True
        },
        {
            "id": "bulk_discount",
            "name": "Giảm giá số lượng lớn",
            "description": "Giảm 15% cho đơn hàng từ 10,000 đơn vị trở lên",
            "discount_percentage": 15,
            "is_active": True
        }
    ]

# Admin Dashboard API Endpoints
@app.get("/api/admin/stats")
async def get_admin_stats():
    """Lấy thống kê tổng quan cho admin dashboard"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Đếm tổng users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    # Đếm tổng orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    # Tính tổng revenue
    cursor.execute("SELECT SUM(price) FROM orders WHERE status = 'completed'")
    total_revenue = cursor.fetchone()[0] or 0
    
    # Kiểm tra API status
    api_status = "Online"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BUMX_API_URL,
                data={"key": BUMX_API_KEY, "action": "balance"},
                timeout=5.0
            )
            if response.status_code != 200:
                api_status = "Offline"
    except:
        api_status = "Offline"
    
    conn.close()
    
    return {
        "totalUsers": total_users,
        "totalOrders": total_orders,
        "totalRevenue": total_revenue,
        "apiStatus": api_status
    }

@app.get("/api/admin/users")
async def get_admin_users(limit: int = 20, offset: int = 0, search: str = "", status: str = ""):
    """Lấy danh sách users cho admin với pagination và filter"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Build query với filters
    query = "SELECT u.*, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id"
    conditions = []
    params = []
    
    if search:
        conditions.append("u.email LIKE ?")
        params.append(f"%{search}%")
    
    if status == "active":
        conditions.append("u.is_active = 1")
    elif status == "banned":
        conditions.append("u.is_active = 0")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " GROUP BY u.id ORDER BY u.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    users = cursor.fetchall()
    
    # Đếm tổng số users
    count_query = "SELECT COUNT(*) FROM users u"
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    
    cursor.execute(count_query, params[:-2])  # Remove limit and offset
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "users": [
            {
                "id": user[0],
                "email": user[1],
                "balance": user[3],
                "total_spent": user[4],
                "is_active": bool(user[5]),
                "created_at": user[6],
                "order_count": user[7]
            }
            for user in users
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/admin/orders")
async def get_admin_orders(limit: int = 20, offset: int = 0, status: str = "", date_from: str = "", date_to: str = ""):
    """Lấy danh sách orders cho admin với pagination và filter"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Build query với filters
    query = """
        SELECT o.*, u.email as user_email 
        FROM orders o 
        JOIN users u ON o.user_id = u.id
    """
    conditions = []
    params = []
    
    if status:
        conditions.append("o.status = ?")
        params.append(status)
    
    if date_from:
        conditions.append("o.created_at >= ?")
        params.append(date_from)
    
    if date_to:
        conditions.append("o.created_at <= ?")
        params.append(date_to)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY o.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    orders = cursor.fetchall()
    
    # Đếm tổng số orders
    count_query = "SELECT COUNT(*) FROM orders o JOIN users u ON o.user_id = u.id"
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    
    cursor.execute(count_query, params[:-2])  # Remove limit and offset
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "orders": [
            {
                "id": order[0],
                "user_id": order[1],
                "user_email": order[10] if len(order) > 10 else "Unknown",  # user_email from JOIN
                "service_id": order[2],
                "service_name": order[3],
                "link": order[4],
                "quantity": order[5],
                "price": order[6],
                "status": order[7],
                "bumx_order_id": order[8] if len(order) > 8 else None,
                "created_at": order[9] if len(order) > 9 else None
            }
            for order in orders
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/admin/transactions")
async def get_admin_transactions(limit: int = 20, offset: int = 0, type_filter: str = "", date_from: str = "", date_to: str = ""):
    """Lấy danh sách transactions cho admin với pagination và filter"""
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    
    # Build query với filters
    query = """
        SELECT t.*, u.email as user_email 
        FROM transactions t 
        JOIN users u ON t.user_id = u.id
    """
    conditions = []
    params = []
    
    if type_filter:
        conditions.append("t.type = ?")
        params.append(type_filter)
    
    if date_from:
        conditions.append("t.created_at >= ?")
        params.append(date_from)
    
    if date_to:
        conditions.append("t.created_at <= ?")
        params.append(date_to)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY t.created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    
    # Đếm tổng số transactions
    count_query = "SELECT COUNT(*) FROM transactions t JOIN users u ON t.user_id = u.id"
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)
    
    cursor.execute(count_query, params[:-2])  # Remove limit and offset
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "transactions": [
            {
                "id": trans[0],
                "user_id": trans[1],
                "user_email": trans[8] if len(trans) > 8 else "Unknown",  # user_email from JOIN
                "type": trans[2],
                "amount": trans[3],
                "balance_before": trans[4],
                "balance_after": trans[5],
                "description": trans[6],
                "created_at": trans[7]
            }
            for trans in transactions
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/admin/system-info")
async def get_system_info():
    """Lấy thông tin hệ thống"""
    import os
    
    # System uptime
    try:
        uptime_seconds = os.popen('cat /proc/uptime').read().split()[0]
        uptime_hours = int(float(uptime_seconds) / 3600)
    except:
        uptime_hours = 0
    
    # Memory usage (simplified)
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        lines = meminfo.split('\n')
        mem_total = 0
        mem_available = 0
        for line in lines:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
            elif line.startswith('MemAvailable:'):
                mem_available = int(line.split()[1])
        
        if mem_total > 0:
            mem_used = mem_total - mem_available
            mem_percent = (mem_used / mem_total) * 100
            memory_usage = f"{mem_percent:.1f}% ({mem_used // 1024}MB / {mem_total // 1024}MB)"
        else:
            memory_usage = "Unknown"
    except:
        memory_usage = "Unknown"
    
    return {
        "backendStatus": "Online",
        "databaseStatus": "Connected",
        "uptime": f"{uptime_hours} hours",
        "memoryUsage": memory_usage,
        "timestamp": datetime.utcnow().isoformat()
    }

# React-Admin endpoints (keep for compatibility)
@app.get("/api/users")
async def get_users():
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id")
    users = cursor.fetchall()
    conn.close()
    
    return {
        "data": [
            {
                "id": user[0],
                "email": user[1],
                "balance": user[3],
                "total_spent": user[4],
                "is_active": bool(user[5]),
                "created_at": user[6]
            }
            for user in users
        ],
        "total": len(users)
    }

@app.get("/api/orders")
async def get_orders():
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY id")
    orders = cursor.fetchall()
    conn.close()
    
    return {
        "data": [
            {
                "id": order[0],
                "user_id": order[1],
                "service_id": order[2],
                "service_name": order[3],
                "link": order[4],
                "quantity": order[5],
                "price": order[6],
                "status": order[7],
                "bumx_order_id": order[8],
                "created_at": order[9],
                "completed_at": order[10]
            }
            for order in orders
        ],
        "total": len(orders)
    }

@app.get("/api/transactions")
async def get_transactions():
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id")
    transactions = cursor.fetchall()
    conn.close()
    
    return {
        "data": [
            {
                "id": trans[0],
                "user_id": trans[1],
                "type": trans[2],
                "amount": trans[3],
                "balance_before": trans[4],
                "balance_after": trans[5],
                "description": trans[6],
                "created_at": trans[7]
            }
            for trans in transactions
        ],
        "total": len(transactions)
    }

# Khởi tạo database khi start
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("SMM Panel Backend started successfully")

if __name__ == "__main__":
    import sys
    port = 80 if "--port" in sys.argv and "80" in sys.argv else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
