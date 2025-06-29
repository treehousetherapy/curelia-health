"""
Audit log model for HIPAA-compliant activity tracking
Records all system access and data modifications
"""

import enum
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class AuditAction(enum.Enum):
    """Types of actions that can be audited"""
    # Authentication actions
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    
    # Access actions
    ACCESS = "access"           # Viewed data
    ACCESS_DENIED = "access_denied"
    EXPORT = "export"           # Exported data
    PRINT = "print"             # Printed data
    
    # Data modification actions
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"         # Undelete
    
    # EVV actions
    CLOCK_IN = "clock_in"
    CLOCK_OUT = "clock_out"
    EVV_OVERRIDE = "evv_override"
    
    # Administrative actions
    CONFIGURATION = "configuration"
    SYSTEM = "system"


class AuditLog(BaseModel):
    """
    Audit log model for HIPAA-compliant activity tracking
    Records all system access and data modifications
    """
    __tablename__ = "audit_logs"
    
    # Who performed the action
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=True,  # Can be null for system actions or failed logins
        index=True,
        comment="User who performed the action"
    )
    
    # What action was performed
    action = Column(
        Enum(AuditAction),
        nullable=False,
        index=True,
        comment="Type of action performed"
    )
    
    # What resource was affected
    resource_type = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Type of resource affected (e.g., User, Client, TimeLog)"
    )
    
    resource_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of resource affected"
    )
    
    # Description of the action
    description = Column(
        Text,
        nullable=False,
        comment="Human-readable description of the action"
    )
    
    # Context information
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP address where action originated"
    )
    
    user_agent = Column(
        String(255),
        nullable=True,
        comment="User agent (browser/app) information"
    )
    
    request_id = Column(
        String(50),
        nullable=True,
        comment="Request ID for tracing"
    )
    
    # Additional data
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional context data about the action"
    )
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action.value} on {self.resource_type}>"
    
    @classmethod
    def log(
        cls,
        session,
        action: AuditAction,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: str = "",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "AuditLog":
        """Create and save an audit log entry"""
        audit_log = cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            metadata=metadata,
        )
        session.add(audit_log)
        return audit_log 