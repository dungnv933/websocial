"""
Configuration settings cho SMM Panel Backend
Load environment variables và validate settings
"""

from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """
    Application settings được load từ environment variables
    """
    
    # App settings
    DEBUG: bool = True
    APP_NAME: str = "SMM Panel Backend"
    VERSION: str = "1.0.0"
    
    # Database settings
    DATABASE_URL: str = "postgresql://smm_user:password123@localhost:5432/smm_panel"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # BUMX API settings
    BUMX_API_URL: str = "https://api-v2.bumx.vn/api/v2"
    BUMX_API_KEY: str = "4b45e706-ec05-45d2-bfb5-2efa54e4d84d"
    
    # JWT settings
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 43200  # 30 days
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["https://smm-panel.yourdomain.com", "https://admin.smm-panel.yourdomain.com"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """
        Parse CORS origins từ string thành list
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()