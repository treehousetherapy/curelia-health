"""
Database initialization module
Creates initial database objects and seed data
"""

import logging
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app import models
from app.core.security import get_password_hash
from app.models.user import UserRole

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Initialize database with seed data"""
    # Create admin user if it doesn't exist
    create_initial_admin(db)
    
    # Create initial reference data
    create_reference_data(db)


def create_initial_admin(db: Session) -> None:
    """Create initial admin user if not exists"""
    admin_email = "admin@curelia.health"
    
    # Check if admin exists
    admin = db.query(models.User).filter(models.User.email == admin_email).first()
    if admin:
        logger.info("Admin user already exists")
        return
    
    # Create admin user
    admin_user = models.User(
        email=admin_email,
        hashed_password=get_password_hash("admin"),  # Change in production
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    
    db.add(admin_user)
    db.commit()
    logger.info("Created admin user")


def create_reference_data(db: Session) -> None:
    """Create reference data needed for application"""
    # Add any reference data here, such as:
    # - Service types
    # - Certification types
    # - Default document templates
    # - etc.
    
    # Example: Create service types if they don't exist
    service_types = [
        "Personal Care",
        "Companionship",
        "Medication Reminder",
        "Light Housekeeping",
        "Meal Preparation",
        "Transportation",
        "Respite Care",
        "Specialized Care",
    ]
    
    for service_name in service_types:
        service = db.query(models.ServiceType).filter(models.ServiceType.name == service_name).first()
        if not service:
            service = models.ServiceType(name=service_name)
            db.add(service)
    
    db.commit()
    logger.info("Created reference data") 