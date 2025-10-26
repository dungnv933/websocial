"""
SMM Panel Backend - Simple Version
Sử dụng SQLite thay vì PostgreSQL để dễ deploy
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
import httpx
import json
import sqlite3
import os

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cấu hình
SECRET_KEY = "thay-bang-random-string-dai-phuc-tap-an-toan-2024-smm-panel-backend"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200
BUMX_API_URL = "https://api-v2.bumx.vn/api/v2"
BUMX_API_KEY = "4b45e706-ec05-45d2-bfb5-2efa54e4d84d"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Tạo FastAPI app
app = FastAPI(
    title="SMM Panel Backend",
    description="Backend API cho SMM Panel - Social Media Marketing Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://social.homemmo.store", "https://app.homemmo.store", "https://api.homemmo.store"],
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
            password_hash TEXT NOT NULL,
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

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        return user_id
    except JWTError:
        return None

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
    return {"message": "SMM Panel Backend API", "docs": "/docs"}

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
    hashed_password = get_password_hash(user_data.password)
    cursor.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (user_data.email, hashed_password)
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
    cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (user_credentials.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(user_credentials.password, user[1]):
        raise HTTPException(status_code=401, detail="Email hoặc password không đúng")
    
    # Tạo token
    access_token = create_access_token(data={"sub": user[0]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/api/services")
async def get_services():
    services = await get_bumx_services()
    return {"services": services, "total": len(services)}

@app.get("/api/balance")
async def get_balance(user_id: int = Depends(lambda: 1)):  # Mock user_id
    conn = sqlite3.connect('smm_panel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"balance": result[0], "currency": "USD"}

@app.post("/api/balance/deposit")
async def deposit_balance(deposit_data: DepositRequest, user_id: int = Depends(lambda: 1)):
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
async def create_order(order_data: OrderCreate, user_id: int = Depends(lambda: 1)):
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
async def get_order_history(user_id: int = Depends(lambda: 1)):
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

# Khởi tạo database khi start
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("SMM Panel Backend started successfully")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
