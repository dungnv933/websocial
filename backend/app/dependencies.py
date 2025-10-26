"""
FastAPI dependencies for SMM Panel
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.auth import verify_token, get_current_user_exception

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get current user from JWT token
    """
    username = verify_token(token)
    if username is None:
        raise get_current_user_exception()
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise get_current_user_exception()
    
    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Check if current user is admin
    """
    # For now, check if username is admin
    # In production, you would have an admin role field
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

