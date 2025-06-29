"""
Schemas package for Pydantic models
Imports all schemas for easy access
"""

from .token import Token, TokenPayload
from .user import User, UserCreate, UserUpdate, UserInDB
from .auth import PasswordResetRequest, PasswordChange
from .caregiver import Caregiver, CaregiverCreate, CaregiverUpdate
from .client import Client, ClientCreate, ClientUpdate
from .timelog import TimeLog, TimeLogCreate, TimeLogUpdate, TimeLogVerify
from .shift import Shift, ShiftCreate, ShiftUpdate, ShiftRecurrence
from .document import Document, DocumentCreate, DocumentUpdate, SignatureCreate

from .dependencies import get_current_user, get_current_active_user, get_current_admin_user

__all__ = [
    # Token schemas
    "Token",
    "TokenPayload",
    
    # User schemas
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    
    # Auth schemas
    "PasswordResetRequest",
    "PasswordChange",
    
    # Caregiver schemas
    "Caregiver",
    "CaregiverCreate",
    "CaregiverUpdate",
    
    # Client schemas
    "Client",
    "ClientCreate",
    "ClientUpdate",
    
    # TimeLog schemas
    "TimeLog",
    "TimeLogCreate",
    "TimeLogUpdate",
    "TimeLogVerify",
    
    # Shift schemas
    "Shift",
    "ShiftCreate",
    "ShiftUpdate",
    "ShiftRecurrence",
    
    # Document schemas
    "Document",
    "DocumentCreate",
    "DocumentUpdate",
    "SignatureCreate",
    
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
] 