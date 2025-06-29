"""
Authentication schemas for password management
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field


class PasswordResetRequest(BaseModel):
    """
    Schema for password reset request
    """
    email: EmailStr


class PasswordReset(BaseModel):
    """
    Schema for password reset with token
    """
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator("new_password")
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class PasswordChange(BaseModel):
    """
    Schema for password change
    """
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator("new_password")
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v 