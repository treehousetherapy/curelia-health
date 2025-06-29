"""
Patient model for healthcare data management
HIPAA-compliant Protected Health Information (PHI) storage
"""

import enum
from datetime import date
from typing import Optional, List
import uuid

from sqlalchemy import Column, String, Date, Enum, Text, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, AuditMixin


class PatientStatus(enum.Enum):
    """Patient status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCHARGED = "discharged"
    DECEASED = "deceased"


class Gender(enum.Enum):
    """Gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class MaritalStatus(enum.Enum):
    """Marital status enumeration"""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"
    OTHER = "other"


class Patient(BaseModel, AuditMixin):
    """
    Patient model containing Protected Health Information (PHI)
    HIPAA-compliant patient data storage
    """
    __tablename__ = "patients"
    
    # Link to User account (if patient has login access)
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=True,
        index=True,
        comment="Reference to user account if patient has login access"
    )
    
    # Basic Demographics (PHI)
    first_name = Column(
        String(100), 
        nullable=False,
        comment="Patient's first name"
    )
    
    last_name = Column(
        String(100), 
        nullable=False,
        comment="Patient's last name"
    )
    
    middle_name = Column(
        String(100), 
        nullable=True,
        comment="Patient's middle name"
    )
    
    date_of_birth = Column(
        Date, 
        nullable=False,
        comment="Patient's date of birth"
    )
    
    gender = Column(
        Enum(Gender), 
        nullable=False,
        comment="Patient's gender"
    )
    
    # Contact Information (PHI)
    phone_primary = Column(
        String(20), 
        nullable=True,
        comment="Primary phone number"
    )
    
    phone_secondary = Column(
        String(20), 
        nullable=True,
        comment="Secondary phone number"
    )
    
    email = Column(
        String(255), 
        nullable=True,
        comment="Email address"
    )
    
    # Address Information (PHI)
    address_line1 = Column(
        String(255), 
        nullable=True,
        comment="Primary address line"
    )
    
    address_line2 = Column(
        String(255), 
        nullable=True,
        comment="Secondary address line (apt, suite, etc.)"
    )
    
    city = Column(
        String(100), 
        nullable=True,
        comment="City"
    )
    
    state = Column(
        String(50), 
        nullable=True,
        comment="State or province"
    )
    
    zip_code = Column(
        String(20), 
        nullable=True,
        comment="ZIP or postal code"
    )
    
    country = Column(
        String(100), 
        nullable=True, 
        default="United States",
        comment="Country"
    )
    
    # Additional demographic information
    ssn_last_four = Column(
        String(4),
        nullable=True,
        comment="Last four digits of SSN (for identification purposes)"
    )
    
    marital_status = Column(
        Enum(MaritalStatus),
        nullable=True,
        comment="Marital status"
    )
    
    # Medical Information
    medical_record_number = Column(
        String(50), 
        unique=True, 
        nullable=True,
        comment="Unique medical record number"
    )
    
    primary_diagnosis = Column(
        Text, 
        nullable=True,
        comment="Primary medical diagnosis"
    )
    
    secondary_diagnoses = Column(
        JSONB, 
        nullable=True,
        comment="Secondary medical diagnoses (JSON array)"
    )
    
    allergies = Column(
        JSONB, 
        nullable=True,
        comment="Known allergies and reactions (JSON array)"
    )
    
    medications = Column(
        JSONB, 
        nullable=True,
        comment="Current medications (JSON array)"
    )
    
    medical_history = Column(
        Text, 
        nullable=True,
        comment="Relevant medical history"
    )
    
    # Care Information
    care_level = Column(
        String(50), 
        nullable=True,
        comment="Level of care required"
    )
    
    care_plan = Column(
        Text, 
        nullable=True,
        comment="Current care plan"
    )
    
    mobility_status = Column(
        String(100), 
        nullable=True,
        comment="Patient mobility status"
    )
    
    dietary_restrictions = Column(
        JSONB, 
        nullable=True,
        comment="Dietary restrictions and preferences (JSON array)"
    )
    
    # Insurance Information
    insurance_provider = Column(
        String(200), 
        nullable=True,
        comment="Primary insurance provider"
    )
    
    insurance_policy_number = Column(
        String(100), 
        nullable=True,
        comment="Insurance policy number"
    )
    
    insurance_group_number = Column(
        String(100), 
        nullable=True,
        comment="Insurance group number"
    )
    
    secondary_insurance_provider = Column(
        String(200), 
        nullable=True,
        comment="Secondary insurance provider"
    )
    
    secondary_insurance_policy_number = Column(
        String(100), 
        nullable=True,
        comment="Secondary insurance policy number"
    )
    
    # Status and Flags
    status = Column(
        Enum(PatientStatus), 
        default=PatientStatus.ACTIVE, 
        nullable=False,
        comment="Patient status"
    )
    
    is_high_risk = Column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="High-risk patient flag"
    )
    
    requires_special_care = Column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="Requires special care attention"
    )
    
    # Admission/Discharge Information
    admission_date = Column(
        Date, 
        nullable=True,
        comment="Date of admission to care"
    )
    
    discharge_date = Column(
        Date, 
        nullable=True,
        comment="Date of discharge from care"
    )
    
    discharge_reason = Column(
        Text, 
        nullable=True,
        comment="Reason for discharge"
    )
    
    # Relationships
    user = relationship("User", back_populates="patient")
    contacts = relationship("PatientContact", back_populates="patient", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="patient")
    documents = relationship("Document", back_populates="patient")
    
    @property
    def full_name(self) -> str:
        """Get patient's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> Optional[int]:
        """Calculate patient's current age"""
        if not self.date_of_birth:
            return None
        
        today = date.today()
        age = today.year - self.date_of_birth.year
        
        # Adjust if birthday hasn't occurred this year
        if today.month < self.date_of_birth.month or \
           (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
            
        return age
    
    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            f"{self.state} {self.zip_code}" if self.state and self.zip_code else self.state or self.zip_code,
            self.country if self.country != "United States" else None
        ]
        return ", ".join(filter(None, address_parts))
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.full_name})>"


class PatientContact(BaseModel, AuditMixin):
    """
    Patient emergency and family contacts
    HIPAA-compliant contact information
    """
    __tablename__ = "patient_contacts"
    
    # Link to patient
    patient_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("patients.id"), 
        nullable=False,
        index=True,
        comment="Reference to patient"
    )
    
    # Contact Information
    first_name = Column(
        String(100), 
        nullable=False,
        comment="Contact's first name"
    )
    
    last_name = Column(
        String(100), 
        nullable=False,
        comment="Contact's last name"
    )
    
    relationship = Column(
        String(50), 
        nullable=False,
        comment="Relationship to patient (spouse, child, parent, etc.)"
    )
    
    phone_primary = Column(
        String(20), 
        nullable=False,
        comment="Primary phone number"
    )
    
    phone_secondary = Column(
        String(20), 
        nullable=True,
        comment="Secondary phone number"
    )
    
    email = Column(
        String(255), 
        nullable=True,
        comment="Email address"
    )
    
    # Address (optional)
    address_line1 = Column(
        String(255), 
        nullable=True,
        comment="Primary address line"
    )
    
    address_line2 = Column(
        String(255), 
        nullable=True,
        comment="Secondary address line"
    )
    
    city = Column(
        String(100), 
        nullable=True,
        comment="City"
    )
    
    state = Column(
        String(50), 
        nullable=True,
        comment="State"
    )
    
    zip_code = Column(
        String(20), 
        nullable=True,
        comment="ZIP code"
    )
    
    # Contact Preferences
    is_emergency_contact = Column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="Primary emergency contact"
    )
    
    is_authorized_contact = Column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="Authorized to receive medical information"
    )
    
    contact_priority = Column(
        Integer, 
        default=1, 
        nullable=False,
        comment="Contact priority order (1 = highest)"
    )
    
    # Relationship
    patient = relationship("Patient", back_populates="contacts")
    
    @property
    def full_name(self) -> str:
        """Get contact's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<PatientContact(id={self.id}, name={self.full_name}, relationship={self.relationship})>" 