"""
SMM Panel Backend - FastAPI Application
Main entry point cho SMM Panel backend service
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.database import engine, Base
from app.api import auth, services, orders, balance, promotions

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager để quản lý startup và shutdown events
    """
    # Startup
    logger.info("🚀 Starting SMM Panel Backend...")
    
    # Tạo database tables nếu chưa tồn tại
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise
    
    logger.info("✅ SMM Panel Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down SMM Panel Backend...")
    await engine.dispose()
    logger.info("✅ SMM Panel Backend shutdown complete")


# Tạo FastAPI application
app = FastAPI(
    title="SMM Panel Backend",
    description="Backend API cho SMM Panel - Social Media Marketing Platform tích hợp BUMX API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Cấu hình CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Xử lý HTTP exceptions với logging
    """
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Xử lý general exceptions với logging
    """
    logger.error(f"Unhandled exception: {str(exc)} - Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint để kiểm tra trạng thái service
    """
    return {
        "status": "healthy",
        "service": "SMM Panel Backend",
        "version": "1.0.0",
        "environment": "development" if settings.DEBUG else "production"
    }


# Root endpoint
@app.get("/")
async def root() -> dict:
    """
    Root endpoint với thông tin API
    """
    return {
        "message": "SMM Panel Backend API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "health": "/health"
    }


# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(balance.router, prefix="/api/balance", tags=["Balance"])
app.include_router(promotions.router, prefix="/api/promotions", tags=["Promotions"])


if __name__ == "__main__":
    """
    Chạy application với uvicorn server
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )