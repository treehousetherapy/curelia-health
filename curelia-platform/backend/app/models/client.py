"""
Client model for storing client information
Manages client profiles, care plans, and service needs
"""

import enum
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey, Text, Enum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from .base import BaseModel


class ClientStatus(enum.Enum):
    """Status of a client"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ON_HOLD = "on_hold"
    DISCHARGED = "discharged"


class Client(BaseModel):
    """
    Client model for storing client information
    Used for service delivery, scheduling, and billing
    """
    __tablename__ = "clients"
    
    # Link to User account (if client has login access)
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=True,
        unique=True,
        comment="Reference to user account (if client has login access)"
    )
    
    # Basic Information
    first_name = Column(
        String(100), 
        nullable=False,
        comment="Client's first name"
    )
    
    last_name = Column(
        String(100), 
        nullable=False,
        comment="Client's last name"
    )
    
    date_of_birth = Column(
        Date, 
        nullable=False,
        comment="Client's date of birth"
    )
    
    gender = Column(
        String(50),
        nullable=True,
        comment="Client's gender"
    )
    
    # Contact Information
    phone_number = Column(
        String(20), 
        nullable=True,
        comment="Primary phone number"
    )
    
    email = Column(
        String(255), 
        nullable=True,
        comment="Email address"
    )
    
    # Service Address
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
    
    # Geolocation for EVV
    latitude = Column(
        Float,
        nullable=True,
        comment="Latitude of client's address"
    )
    
    longitude = Column(
        Float,
        nullable=True,
        comment="Longitude of client's address"
    )
    
    location = Column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True,
        comment="Geographic point for spatial queries"
    )
    
    geofence_radius_meters = Column(
        Integer,
        nullable=False,
        default=100,
        comment="Radius in meters for EVV geofence"
    )
    
    # Client Status and Service Information
    status = Column(
        Enum(ClientStatus),
        nullable=False,
        default=ClientStatus.PENDING,
        comment="Current client status"
    )
    
    client_id = Column(
        String(50), 
        nullable=True,
        unique=True,
        comment="Client ID number"
    )
    
    start_of_care = Column(
        Date, 
        nullable=True,
        comment="Date client started receiving services"
    )
    
    end_of_care = Column(
        Date, 
        nullable=True,
        comment="Date client stopped receiving services (if applicable)"
    )
    
    # Service Details
    service_types = Column(
        ARRAY(String),
        nullable=True,
        comment="Types of services client receives"
    )
    
    service_hours_per_week = Column(
        Float,
        nullable=True,
        comment="Authorized service hours per week"
    )
    
    care_level = Column(
        String(50),
        nullable=True,
        comment="Level of care required"
    )
    
    # Insurance and Billing
    primary_insurance = Column(
        String(100),
        nullable=True,
        comment="Primary insurance provider"
    )
    
    insurance_id = Column(
        String(100),
        nullable=True,
        comment="Insurance ID number"
    )
    
    insurance_group = Column(
        String(100),
        nullable=True,
        comment="Insurance group number"
    )
    
    medicaid_id = Column(
        String(100),
        nullable=True,
        comment="Medicaid ID number"
    )
    
    medicare_id = Column(
        String(100),
        nullable=True,
        comment="Medicare ID number"
    )
    
    evv_required = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether EVV is required for this client"
    )
    
    billing_type = Column(
        String(50),
        nullable=True,
        comment="Type of billing (private, insurance, medicaid, etc.)"
    )
    
    billing_rate = Column(
        Float,
        nullable=True,
        comment="Billing rate per hour"
    )
    
    # Care Information
    diagnosis = Column(
        JSONB,
        nullable=True,
        comment="Client diagnoses"
    )
    
    allergies = Column(
        ARRAY(String),
        nullable=True,
        comment="Client allergies"
    )
    
    mobility_status = Column(
        String(100),
        nullable=True,
        comment="Client mobility status"
    )
    
    # Emergency Contacts
    emergency_contacts = Column(
        JSONB,
        nullable=True,
        comment="Emergency contacts information"
    )
    
    # Additional Information
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes about the client"
    )
    
    preferences = Column(
        JSONB,
        nullable=True,
        comment="Client preferences"
    )
    
    # Relationships
    user = relationship("User", back_populates="client_profile")
    shifts = relationship("Shift", back_populates="client")
    timelogs = relationship("TimeLog", back_populates="client")
    care_plans = relationship("CarePlan", back_populates="client")
    
    def __repr__(self):
        return f"<Client {self.id}: {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self) -> str:
        """Get client's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calculate client's age"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_active(self) -> bool:
        """Check if client is active"""
        return self.status == ClientStatus.ACTIVE
    
    @property
    def full_address(self) -> str:
        """Get client's full address"""
        address = f"{self.address_line1}"
        if self.address_line2:
            address += f", {self.address_line2}"
        address += f", {self.city}, {self.state} {self.zip_code}"
        return address


class CarePlan(BaseModel):
    """
    CarePlan model for storing client care plans
    Used for service delivery and compliance
    """
    __tablename__ = "care_plans"
    
    client_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("clients.id"), 
        nullable=False,
        index=True,
        comment="Reference to client"
    )
    
    title = Column(
        String(255),
        nullable=False,
        comment="Care plan title"
    )
    
    start_date = Column(
        Date,
        nullable=False,
        comment="Start date of care plan"
    )
    
    end_date = Column(
        Date,
        nullable=True,
        comment="End date of care plan (if applicable)"
    )
    
    goals = Column(
        JSONB,
        nullable=True,
        comment="Care plan goals"
    )
    
    interventions = Column(
        JSONB,
        nullable=True,
        comment="Care plan interventions"
    )
    
    service_details = Column(
        JSONB,
        nullable=True,
        comment="Detailed service requirements"
    )
    
    created_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        comment="User who created the care plan"
    )
    
    approved_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=True,
        comment="User who approved the care plan"
    )
    
    approved_at = Column(
        DateTime,
        nullable=True,
        comment="When the care plan was approved"
    )
    
    document_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("documents.id"), 
        nullable=True,
        comment="Reference to uploaded care plan document"
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes about the care plan"
    )
    
    # Relationships
    client = relationship("Client", back_populates="care_plans")
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    document = relationship("Document")
    
    def __repr__(self):
        return f"<CarePlan {self.id}: {self.title} for {self.client_id}>"
    
    @property
    def is_active(self) -> bool:
        """Check if care plan is currently active"""
        today = date.today()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date <= today
    
    @property
    def is_approved(self) -> bool:
        """Check if care plan is approved"""
        return self.approved_by_id is not None and self.approved_at is not None 