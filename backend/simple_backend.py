# -*- coding: utf-8 -*-
"""
Simple FastAPI Backend for SMM Panel
Compatible with Python 3.6 and existing packages
"""
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
import json
from datetime import datetime
from typing import Optional, List
import httpx
from services_manager import service_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="SMM Panel API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = "smm_panel.db"

def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            balance REAL DEFAULT 0,
            total_spent REAL DEFAULT 0,
            tier_level INTEGER DEFAULT 1,
            tier_name TEXT DEFAULT 'Cap 1',
            tier_discount REAL DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by_code TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            link TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            charge REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            start_count INTEGER DEFAULT 0,
            remains INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Pydantic models
class UserCreate(BaseModel):
    username = str
    email = str
    password = str
    referral_code = str

class UserLogin(BaseModel):
    username = str
    password = str

class OrderCreate(BaseModel):
    service_id = int
    link = str
    quantity = int

# Initialize database
init_db()

# API Endpoints

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "SMM Panel API", "status": "running"}

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/admin/stats")
def get_admin_stats():
    """Get admin dashboard statistics"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get user count
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()["count"]
    
    # Get order count
    cursor.execute("SELECT COUNT(*) as count FROM orders")
    order_count = cursor.fetchone()["count"]
    
    # Get total revenue
    cursor.execute("SELECT SUM(charge) as total FROM orders WHERE status = 'completed'")
    total_revenue = cursor.fetchone()["total"] or 0
    
    conn.close()
    
    return {
        "users": user_count,
        "orders": order_count,
        "revenue": total_revenue,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/users")
def get_users():
    """Get all users"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, email, balance, total_spent, 
               tier_level, tier_name, status, created_at
        FROM users 
        ORDER BY created_at DESC
    """)
    
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"users": users}

@app.get("/api/orders")
def get_orders():
    """Get all orders"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT o.id, o.user_id, u.username, o.service_id, o.link, 
               o.quantity, o.charge, o.status, o.start_count, o.remains,
               o.created_at, o.updated_at
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    """)
    
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"orders": orders}

# === SERVICES MANAGEMENT ENDPOINTS ===

@app.post("/api/services/sync")
def sync_services():
    """Sync services from Likeviet API"""
    result = service_manager.sync_services_from_likeviet()
    return result

@app.get("/api/services")
def get_services(
    category = None,
    platform = None,
    enabled_only = True,
    search = None
):
    """Get all services with filters"""
    print("[API] GET /api/services")
    print("[API] category=" + str(category))
    print("[API] platform=" + str(platform))
    print("[API] search=" + str(search))
    
    try:
        if search:
            services = service_manager.search_services(search)
        else:
            services = service_manager.get_all_services(
                enabled_only=enabled_only,
                category=category,
                platform=platform
            )
        
        print("[API] Returning " + str(len(services)) + " services")
        return {"services": services, "count": len(services)}
    
    except Exception as e:
        print("[API] Error: " + str(e))
        return {"services": [], "error": str(e)}

@app.get("/api/services/categories")
def get_categories():
    """Get all service categories with counts"""
    print("[API] GET /api/services/categories")
    try:
        categories = service_manager.get_categories()
        return {"categories": categories}
    except Exception as e:
        print("[API] Error: " + str(e))
        return {"categories": [], "error": str(e)}

@app.get("/api/services/platforms")
def get_platforms():
    """Get all platforms"""
    print("[API] GET /api/services/platforms")
    platforms = service_manager.get_platforms()
    return {"platforms": platforms}

@app.get("/api/services/{likeviet_id}")
def get_service(likeviet_id):
    """Get service by Likeviet ID"""
    print("[API] GET /api/services/{}".format(likeviet_id))
    service = service_manager.get_service_by_id(likeviet_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@app.put("/api/services/{likeviet_id}/markup")
def update_service_markup(likeviet_id, markup_percent):
    """Update service markup percentage"""
    print("[API] PUT /api/services/{}/markup - {}%".format(likeviet_id, markup_percent))
    success = service_manager.update_service_markup(likeviet_id, markup_percent)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"success": True, "markup_percent": markup_percent}

@app.put("/api/services/{likeviet_id}/toggle")
def toggle_service_status(likeviet_id):
    """Toggle service active status"""
    print("[API] PUT /api/services/{}/toggle".format(likeviet_id))
    success = service_manager.toggle_service(likeviet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"success": True}

# === LIKEVIET API ENDPOINTS ===

LIKEVIET_API_BASE = "https://likeviet.vn/api/v2"
LIKEVIET_API_KEY = "c827f930b6fbe6dc726f5ed7429b31b7"

@app.get("/api/likeviet/balance")
def get_likeviet_balance():
    """Get Likeviet account balance"""
    print("[API] GET /api/likeviet/balance")
    
    payload = {
        "key": LIKEVIET_API_KEY,
        "action": "balance"
    }
    
    try:
        response = httpx.post(LIKEVIET_API_BASE, data=payload, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": "Request failed: {}".format(str(e))}

@app.get("/api/likeviet/services")
def get_likeviet_services():
    """Get available services from Likeviet"""
    print("[API] GET /api/likeviet/services")
    
    payload = {
        "key": LIKEVIET_API_KEY,
        "action": "services"
    }
    
    try:
        response = httpx.post(LIKEVIET_API_BASE, data=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": "Request failed: {}".format(str(e))}

@app.post("/api/likeviet/order")
def create_likeviet_order(service_id, link, quantity):
    """Create new Likeviet order"""
    print("[API] POST /api/likeviet/order - service_id={}, quantity={}".format(service_id, quantity))
    
    payload = {
        "key": LIKEVIET_API_KEY,
        "action": "add",
        "service": service_id,
        "link": link,
        "quantity": quantity
    }
    
    try:
        response = httpx.post(LIKEVIET_API_BASE, data=payload, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": "Request failed: {}".format(str(e))}

@app.get("/api/likeviet/order/{order_id}")
def get_order_status(order_id):
    """Check Likeviet order status"""
    print("[API] GET /api/likeviet/order/{}".format(order_id))
    
    payload = {
        "key": LIKEVIET_API_KEY,
        "action": "status",
        "order": order_id
    }
    
    try:
        response = httpx.post(LIKEVIET_API_BASE, data=payload, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": "Request failed: {}".format(str(e))}

if __name__ == "__main__":
    import httpx
    uvicorn.run(app, host="0.0.0.0", port=8000)