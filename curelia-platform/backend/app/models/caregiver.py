"""
Caregiver model for storing caregiver information
Manages caregiver profiles, credentials, and availability
"""

import enum
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey, Text, Enum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from .base import BaseModel


class CaregiverStatus(enum.Enum):
    """Status of a caregiver"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class EmploymentType(enum.Enum):
    """Employment type of a caregiver"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"


class Caregiver(BaseModel):
    """
    Caregiver model for storing caregiver information
    Used for scheduling, EVV, and payroll
    """
    __tablename__ = "caregivers"
    
    # Link to User account
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        unique=True,
        comment="Reference to user account"
    )
    
    # Basic Information
    first_name = Column(
        String(100), 
        nullable=False,
        comment="Caregiver's first name"
    )
    
    last_name = Column(
        String(100), 
        nullable=False,
        comment="Caregiver's last name"
    )
    
    date_of_birth = Column(
        Date, 
        nullable=False,
        comment="Caregiver's date of birth"
    )
    
    ssn_last_four = Column(
        String(4), 
        nullable=True,
        comment="Last four digits of SSN (encrypted at rest)"
    )
    
    # Contact Information
    phone_number = Column(
        String(20), 
        nullable=False,
        comment="Primary phone number"
    )
    
    email = Column(
        String(255), 
        nullable=False,
        unique=True,
        comment="Email address"
    )
    
    # Address
    address_line1 = Column(
        String(255), 
        nullable=False,
        comment="Street address line 1"
    )
    
    address_line2 = Column(
        String(255), 
        nullable=True,
        comment="Street address line 2"
    )
    
    city = Column(
        String(100), 
        nullable=False,
        comment="City"
    )
    
    state = Column(
        String(2), 
        nullable=False,
        comment="State (2-letter code)"
    )
    
    zip_code = Column(
        String(10), 
        nullable=False,
        comment="ZIP code"
    )
    
    # Employment Details
    employee_id = Column(
        String(50), 
        nullable=True,
        unique=True,
        comment="Employee ID number"
    )
    
    status = Column(
        Enum(CaregiverStatus),
        nullable=False,
        default=CaregiverStatus.PENDING,
        comment="Current employment status"
    )
    
    employment_type = Column(
        Enum(EmploymentType),
        nullable=False,
        default=EmploymentType.PART_TIME,
        comment="Type of employment"
    )
    
    hire_date = Column(
        Date, 
        nullable=True,
        comment="Date caregiver was hired"
    )
    
    termination_date = Column(
        Date, 
        nullable=True,
        comment="Date caregiver was terminated (if applicable)"
    )
    
    # Pay Information
    pay_rate = Column(
        Float,
        nullable=True,
        comment="Base hourly pay rate"
    )
    
    pay_rates = Column(
        JSONB,
        nullable=True,
        comment="Service-specific pay rates"
    )
    
    # Qualifications and Skills
    qualifications = Column(
        JSONB,
        nullable=True,
        comment="Qualifications and certifications"
    )
    
    skills = Column(
        ARRAY(String),
        nullable=True,
        comment="List of skills and specialties"
    )
    
    languages = Column(
        ARRAY(String),
        nullable=True,
        comment="Languages spoken"
    )
    
    # Scheduling Preferences
    availability = Column(
        JSONB,
        nullable=True,
        comment="Weekly availability schedule"
    )
    
    max_hours_per_week = Column(
        Integer,
        nullable=True,
        comment="Maximum hours per week"
    )
    
    preferred_clients = Column(
        ARRAY(UUID),
        nullable=True,
        comment="Preferred clients to work with"
    )
    
    preferred_distance = Column(
        Integer,
        nullable=True,
        comment="Maximum travel distance (miles)"
    )
    
    # Compliance and Credentials
    background_check_date = Column(
        Date,
        nullable=True,
        comment="Date of last background check"
    )
    
    background_check_status = Column(
        String(50),
        nullable=True,
        comment="Status of background check"
    )
    
    has_drivers_license = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether caregiver has a valid driver's license"
    )
    
    has_vehicle = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether caregiver has their own vehicle"
    )
    
    has_vehicle_insurance = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether caregiver has vehicle insurance"
    )
    
    # Additional Information
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes about the caregiver"
    )
    
    # Relationships
    user = relationship("User", back_populates="caregiver_profile")
    shifts = relationship("Shift", back_populates="caregiver")
    timelogs = relationship("TimeLog", back_populates="caregiver")
    credentials = relationship("Credential", back_populates="caregiver")
    
    def __repr__(self):
        return f"<Caregiver {self.id}: {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self) -> str:
        """Get caregiver's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calculate caregiver's age"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_active(self) -> bool:
        """Check if caregiver is active"""
        return self.status == CaregiverStatus.ACTIVE
    
    @property
    def full_address(self) -> str:
        """Get caregiver's full address"""
        address = f"{self.address_line1}"
        if self.address_line2:
            address += f", {self.address_line2}"
        address += f", {self.city}, {self.state} {self.zip_code}"
        return address


class Credential(BaseModel):
    """
    Credential model for tracking caregiver credentials
    Used for compliance tracking and expiration alerts
    """
    __tablename__ = "credentials"
    
    caregiver_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("caregivers.id"), 
        nullable=False,
        index=True,
        comment="Reference to caregiver"
    )
    
    credential_type = Column(
        String(100),
        nullable=False,
        comment="Type of credential (license, certification, etc.)"
    )
    
    credential_number = Column(
        String(100),
        nullable=True,
        comment="Credential identifier or number"
    )
    
    issuing_authority = Column(
        String(255),
        nullable=True,
        comment="Authority that issued the credential"
    )
    
    issue_date = Column(
        Date,
        nullable=True,
        comment="Date credential was issued"
    )
    
    expiration_date = Column(
        Date,
        nullable=True,
        index=True,
        comment="Date credential expires"
    )
    
    status = Column(
        String(50),
        nullable=False,
        default="active",
        comment="Current status of credential"
    )
    
    verification_date = Column(
        Date,
        nullable=True,
        comment="Date credential was verified"
    )
    
    verified_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=True,
        comment="User who verified the credential"
    )
    
    document_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("documents.id"), 
        nullable=True,
        comment="Reference to uploaded credential document"
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes about the credential"
    )
    
    # Relationships
    caregiver = relationship("Caregiver", back_populates="credentials")
    verified_by = relationship("User")
    document = relationship("Document")
    
    def __repr__(self):
        return f"<Credential {self.id}: {self.credential_type} for {self.caregiver_id}>"
    
    @property
    def is_expired(self) -> bool:
        """Check if credential is expired"""
        if not self.expiration_date:
            return False
        return date.today() > self.expiration_date
    
    @property
    def days_until_expiration(self) -> Optional[int]:
        """Calculate days until expiration"""
        if not self.expiration_date:
            return None
        delta = self.expiration_date - date.today()
        return delta.days 