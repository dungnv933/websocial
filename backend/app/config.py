"""
Configuration settings for SMM Panel Backend
"""
import os
from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost/smmpanel"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External APIs
    bumx_api_key: str = "your-bumx-api-key"
    bumx_api_url: str = "https://bumx.vn/api/v1"
    sepay_secret: str = "your-sepay-secret"
    
    # Telegram
    telegram_bot_token: str = "your-telegram-bot-token"
    telegram_chat_id: str = "your-chat-id"
    
    # App settings
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "https://social.homemmo.store"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
