"""
Models package for Curelia Health Platform
Imports all models for easy access
"""

from .base import BaseModel, AuditMixin
from .user import User, UserRole
from .caregiver import Caregiver, CaregiverStatus, Certification, CertificationType, CertificationStatus
from .client import Client, ClientStatus, ServiceType, ServiceFrequency, CareLevel
from .timelog import TimeLog, TimeLogStatus, TimeLogVerificationMethod
from .shift import Shift, ShiftStatus, RecurrencePattern
from .document import Document, DocumentType, DocumentStatus, Signature
from .audit import AuditLog, AuditAction

# Export all models
__all__ = [
    # Base models
    'BaseModel',
    'AuditMixin',
    
    # User models
    'User',
    'UserRole',
    
    # Caregiver models
    'Caregiver',
    'CaregiverStatus',
    'Certification',
    'CertificationType',
    'CertificationStatus',
    
    # Client models
    'Client',
    'ClientStatus',
    'ServiceType',
    'ServiceFrequency',
    'CareLevel',
    
    # EVV & Scheduling models
    'TimeLog',
    'TimeLogStatus',
    'TimeLogVerificationMethod',
    'Shift',
    'ShiftStatus',
    'RecurrencePattern',
    
    # Document models
    'Document',
    'DocumentType',
    'DocumentStatus',
    'Signature',
    
    # Audit models
    'AuditLog',
    'AuditAction',
] 