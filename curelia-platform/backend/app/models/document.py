"""
Document model for document vault functionality
Manages secure document storage and e-signatures
"""

import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Enum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from .base import BaseModel, AuditMixin


class DocumentType(enum.Enum):
    """Types of documents in the system"""
    INTAKE_FORM = "intake_form"
    ASSESSMENT = "assessment"
    CARE_PLAN = "care_plan"
    SERVICE_AGREEMENT = "service_agreement"
    MEDICAL_RECORD = "medical_record"
    CREDENTIAL = "credential"
    TRAINING_CERTIFICATE = "training_certificate"
    BACKGROUND_CHECK = "background_check"
    EMPLOYMENT_DOCUMENT = "employment_document"
    INVOICE = "invoice"
    REPORT = "report"
    NOTE = "note"
    OTHER = "other"


class DocumentStatus(enum.Enum):
    """Status of a document"""
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class Document(BaseModel, AuditMixin):
    """
    Document model for secure document storage
    Used for forms, records, and signed documents
    """
    __tablename__ = "documents"
    
    # Document metadata
    title = Column(
        String(255),
        nullable=False,
        comment="Document title"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Document description"
    )
    
    document_type = Column(
        Enum(DocumentType),
        nullable=False,
        index=True,
        comment="Type of document"
    )
    
    status = Column(
        Enum(DocumentStatus),
        nullable=False,
        default=DocumentStatus.DRAFT,
        index=True,
        comment="Current document status"
    )
    
    # File information
    filename = Column(
        String(255),
        nullable=False,
        comment="Original filename"
    )
    
    file_path = Column(
        String(512),
        nullable=False,
        comment="Path to file in storage (S3, GCS, etc.)"
    )
    
    file_size = Column(
        Integer,
        nullable=False,
        comment="File size in bytes"
    )
    
    mime_type = Column(
        String(100),
        nullable=False,
        comment="MIME type of document"
    )
    
    # Ownership and access
    owner_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True,
        comment="User who owns/uploaded the document"
    )
    
    client_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("clients.id"), 
        nullable=True,
        index=True,
        comment="Client associated with document (if applicable)"
    )
    
    caregiver_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("caregivers.id"), 
        nullable=True,
        index=True,
        comment="Caregiver associated with document (if applicable)"
    )
    
    # Access control
    access_level = Column(
        String(50),
        nullable=False,
        default="private",
        comment="Access level (private, shared, public)"
    )
    
    shared_with = Column(
        ARRAY(UUID),
        nullable=True,
        comment="User IDs with whom this document is shared"
    )
    
    # Dates
    uploaded_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="When document was uploaded"
    )
    
    expires_at = Column(
        DateTime,
        nullable=True,
        comment="When document expires (if applicable)"
    )
    
    # E-signature information
    requires_signature = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether document requires signatures"
    )
    
    signature_status = Column(
        JSONB,
        nullable=True,
        comment="Status of required signatures"
    )
    
    completed_at = Column(
        DateTime,
        nullable=True,
        comment="When document was fully signed/completed"
    )
    
    # Additional metadata
    tags = Column(
        ARRAY(String),
        nullable=True,
        comment="Tags for categorization"
    )
    
    form_data = Column(
        JSONB,
        nullable=True,
        comment="Form data for dynamic forms"
    )
    
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional document metadata"
    )
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    client = relationship("Client", back_populates="documents")
    caregiver = relationship("Caregiver")
    signatures = relationship("Signature", back_populates="document")
    
    def __repr__(self):
        return f"<Document {self.id}: {self.title} ({self.document_type.value})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if document is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_signed(self) -> bool:
        """Check if document is fully signed"""
        return self.status == DocumentStatus.SIGNED
    
    @property
    def days_until_expiration(self) -> Optional[int]:
        """Calculate days until expiration"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return delta.days


class Signature(BaseModel):
    """
    Signature model for e-signatures
    Tracks who signed a document and when
    """
    __tablename__ = "signatures"
    
    document_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("documents.id"), 
        nullable=False,
        index=True,
        comment="Document that was signed"
    )
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True,
        comment="User who signed"
    )
    
    signature_data = Column(
        Text,
        nullable=True,
        comment="Signature data (image or text)"
    )
    
    signed_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="When document was signed"
    )
    
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP address where signature originated"
    )
    
    user_agent = Column(
        String(255),
        nullable=True,
        comment="User agent (browser/app) information"
    )
    
    verification_method = Column(
        String(50),
        nullable=False,
        comment="How signer was verified (email, SMS, etc.)"
    )
    
    verification_code = Column(
        String(100),
        nullable=True,
        comment="Code used for verification"
    )
    
    signature_type = Column(
        String(50),
        nullable=False,
        default="electronic",
        comment="Type of signature (electronic, digital, etc.)"
    )
    
    # Relationships
    document = relationship("Document", back_populates="signatures")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Signature {self.id}: {self.user_id} on {self.document_id}>" 