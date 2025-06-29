"""
User schemas for data validation
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, UUID4, validator, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """Schema for user creation"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    role: UserRole
    
    @validator("password")
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserUpdate(UserBase):
    """Schema for user updates"""
    password: Optional[str] = None
    
    @validator("password")
    def password_strength(cls, v):
        """Validate password strength if provided"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserInDB(UserBase):
    """Schema for user in database"""
    id: UUID4
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_verified: bool
    is_locked: bool
    last_login_at: Optional[datetime] = None
    failed_login_attempts: int
    
    class Config:
        orm_mode = True


class User(UserBase):
    """Schema for user responses"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    is_verified: bool
    
    class Config:
        orm_mode = True
        
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}" 