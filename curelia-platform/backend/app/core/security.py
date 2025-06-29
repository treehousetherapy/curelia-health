"""
Security utilities for authentication and authorization
Handles password hashing, JWT tokens, and access control
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.models.audit import AuditAction

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "iat": datetime.utcnow()}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """Authenticate a user by email and password"""
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        # Log failed login attempt
        user.failed_login_attempts += 1
        
        # Lock account after too many failed attempts
        if user.failed_login_attempts >= 5:
            user.is_locked = True
            
        db.commit()
        
        # Log the failed login
        models.AuditLog.log(
            db,
            action=AuditAction.LOGIN_FAILED,
            user_id=user.id,
            description=f"Failed login attempt for {email}",
            resource_type="User",
            resource_id=user.id,
        )
        
        return None
    
    # Check if account is active and not locked
    if not user.is_active or user.is_locked:
        return None
    
    # Check if password is expired
    if user.password_changed_at and settings.HIPAA_PASSWORD_EXPIRY_DAYS:
        days_since_change = (datetime.utcnow() - user.password_changed_at).days
        if days_since_change > settings.HIPAA_PASSWORD_EXPIRY_DAYS:
            return None
    
    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return user


def get_current_user(db: Session, token: str) -> Optional[models.User]:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
            
        # Check token expiration
        if "exp" in payload and payload["exp"] < time.time():
            return None
            
    except jwt.PyJWTError:
        return None
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user or not user.is_active:
        return None
        
    return user 