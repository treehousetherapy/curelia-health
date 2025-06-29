"""
User model for authentication and authorization
Manages user accounts, roles, and authentication
"""

import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel, AuditMixin


class UserRole(enum.Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"           # Full system access
    STAFF = "staff"           # Office staff, schedulers, etc.
    CAREGIVER = "caregiver"   # Field caregivers
    CLIENT = "client"         # Service recipients
    FAMILY = "family"         # Family members of clients


class User(BaseModel, AuditMixin):
    """
    User model for authentication and authorization
    Used for login, permissions, and access control
    """
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(
        String(255), 
        nullable=False,
        unique=True,
        index=True,
        comment="Email address (used for login)"
    )
    
    hashed_password = Column(
        String(255), 
        nullable=False,
        comment="Hashed password"
    )
    
    # User information
    first_name = Column(
        String(100), 
        nullable=False,
        comment="User's first name"
    )
    
    last_name = Column(
        String(100), 
        nullable=False,
        comment="User's last name"
    )
    
    # Role and permissions
    role = Column(
        Enum(UserRole),
        nullable=False,
        comment="User role for permissions"
    )
    
    permissions = Column(
        JSONB,
        nullable=True,
        comment="Custom permissions beyond role"
    )
    
    # Account status
    is_active = Column(
        Boolean, 
        nullable=False, 
        default=True,
        comment="Whether user account is active"
    )
    
    is_verified = Column(
        Boolean, 
        nullable=False, 
        default=False,
        comment="Whether email has been verified"
    )
    
    is_locked = Column(
        Boolean, 
        nullable=False, 
        default=False,
        comment="Whether account is locked due to security"
    )
    
    # Security tracking
    last_login_at = Column(
        DateTime, 
        nullable=True,
        comment="Last successful login timestamp"
    )
    
    last_login_ip = Column(
        String(50), 
        nullable=True,
        comment="IP address of last login"
    )
    
    failed_login_attempts = Column(
        Integer, 
        nullable=False, 
        default=0,
        comment="Count of consecutive failed login attempts"
    )
    
    password_changed_at = Column(
        DateTime, 
        nullable=True,
        comment="When password was last changed"
    )
    
    # Mobile app settings
    fcm_token = Column(
        String(255), 
        nullable=True,
        comment="Firebase Cloud Messaging token for push notifications"
    )
    
    device_id = Column(
        String(255), 
        nullable=True,
        comment="Mobile device identifier"
    )
    
    # Preferences
    timezone = Column(
        String(50), 
        nullable=True, 
        default="UTC",
        comment="User's timezone"
    )
    
    preferences = Column(
        JSONB,
        nullable=True,
        comment="User preferences"
    )
    
    # Relationships
    caregiver_profile = relationship("Caregiver", back_populates="user", uselist=False)
    client_profile = relationship("Client", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User {self.id}: {self.email} ({self.role.value})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an administrator"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_staff(self) -> bool:
        """Check if user is staff"""
        return self.role == UserRole.STAFF
    
    @property
    def is_caregiver(self) -> bool:
        """Check if user is a caregiver"""
        return self.role == UserRole.CAREGIVER
    
    @property
    def is_client(self) -> bool:
        """Check if user is a client"""
        return self.role == UserRole.CLIENT
    
    @property
    def days_since_password_change(self) -> Optional[int]:
        """Calculate days since last password change"""
        if not self.password_changed_at:
            return None
        delta = datetime.utcnow() - self.password_changed_at
        return delta.days 