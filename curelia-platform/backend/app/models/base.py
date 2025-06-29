"""
Base model for all database models
Provides common fields and functionality
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Boolean, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, Session


class Base:
    """Base class for all models"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name"""
        return cls.__name__.lower()


# Create declarative base
BaseModel = declarative_base(cls=Base)


class BaseModel(BaseModel):
    """
    Base model with common fields for all models
    Includes id, timestamps, and soft delete functionality
    """
    __abstract__ = True
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        comment="Unique identifier"
    )
    
    # Timestamps
    created_at = Column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        comment="Creation timestamp"
    )
    
    updated_at = Column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        comment="Last update timestamp"
    )
    
    # Soft delete
    is_deleted = Column(
        Boolean, 
        nullable=False, 
        default=False,
        comment="Soft delete flag"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self) -> str:
        """String representation of model instance"""
        return f"<{self.__class__.__name__} {self.id}>"


class AuditMixin:
    """
    Mixin for audit logging
    Adds created_by and updated_by fields
    """
    created_by_id = Column(
        UUID(as_uuid=True), 
        nullable=True,
        comment="User who created the record"
    )
    
    updated_by_id = Column(
        UUID(as_uuid=True), 
        nullable=True,
        comment="User who last updated the record"
    )


# SQLAlchemy event listeners for soft delete
@event.listens_for(Session, "do_orm_execute")
def _add_soft_delete_filter(execute_state):
    """
    Automatically filter soft-deleted records
    Unless explicitly asked not to with execution_options(include_deleted=True)
    """
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            ~execute_state.statement._where_criteria.contains(BaseModel.is_deleted == True)
        ) 