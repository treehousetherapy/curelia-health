"""
TimeLog model for EVV (Electronic Visit Verification)
Tracks caregiver clock-in/out events with GPS verification
"""

import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from .base import BaseModel


class TimeLogType(enum.Enum):
    """Type of time log entry"""
    CLOCK_IN = "clock_in"
    CLOCK_OUT = "clock_out"
    BREAK_START = "break_start"
    BREAK_END = "break_end"
    MANUAL_ADJUSTMENT = "manual_adjustment"


class TimeLogStatus(enum.Enum):
    """Status of time log entry"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    FLAGGED = "flagged"  # For potential EVV violations
    ADJUSTED = "adjusted"  # After manual review


class TimeLog(BaseModel):
    """
    TimeLog model for tracking caregiver clock-in/out events
    Used for EVV compliance and payroll calculations
    """
    __tablename__ = "timelogs"
    
    # Relationships
    caregiver_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("caregivers.id"), 
        nullable=False,
        index=True,
        comment="Reference to caregiver who logged time"
    )
    
    client_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("clients.id"), 
        nullable=False,
        index=True,
        comment="Reference to client receiving service"
    )
    
    shift_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("shifts.id"), 
        nullable=True,  # Can be null for unscheduled visits
        index=True,
        comment="Reference to scheduled shift (if applicable)"
    )
    
    # Time tracking
    timestamp = Column(
        DateTime, 
        nullable=False,
        index=True,
        comment="When the time event occurred"
    )
    
    log_type = Column(
        Enum(TimeLogType),
        nullable=False,
        comment="Type of time log entry"
    )
    
    # GPS verification
    latitude = Column(
        Float,
        nullable=True,
        comment="GPS latitude where event was logged"
    )
    
    longitude = Column(
        Float,
        nullable=True,
        comment="GPS longitude where event was logged"
    )
    
    location = Column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True,
        comment="Geographic point for spatial queries"
    )
    
    address = Column(
        String(255),
        nullable=True,
        comment="Reverse geocoded address"
    )
    
    accuracy_meters = Column(
        Float,
        nullable=True,
        comment="GPS accuracy in meters"
    )
    
    # Verification
    is_within_geofence = Column(
        Boolean,
        nullable=True,
        comment="Whether log was within client's geofence"
    )
    
    device_id = Column(
        String(255),
        nullable=True,
        comment="Device identifier (phone, tablet, etc.)"
    )
    
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP address where event was logged"
    )
    
    status = Column(
        Enum(TimeLogStatus),
        nullable=False,
        default=TimeLogStatus.PENDING,
        comment="Verification status of the time log"
    )
    
    # Additional data
    notes = Column(
        Text,
        nullable=True,
        comment="Optional notes about the time log"
    )
    
    service_codes = Column(
        JSONB,
        nullable=True,
        comment="Service codes for billing/payroll"
    )
    
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional metadata (device info, etc.)"
    )
    
    # For manual adjustments
    adjusted_by_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=True,
        comment="User who adjusted this record (if applicable)"
    )
    
    adjustment_reason = Column(
        Text,
        nullable=True,
        comment="Reason for manual adjustment"
    )
    
    original_timestamp = Column(
        DateTime, 
        nullable=True,
        comment="Original timestamp before adjustment"
    )
    
    # Relationships
    caregiver = relationship("Caregiver", back_populates="timelogs")
    client = relationship("Client", back_populates="timelogs")
    shift = relationship("Shift", back_populates="timelogs")
    adjusted_by = relationship("User")
    
    def __repr__(self):
        return f"<TimeLog {self.log_type.value} by {self.caregiver_id} for {self.client_id} at {self.timestamp}>"
    
    @property
    def is_verified(self) -> bool:
        """Check if time log is verified"""
        return self.status == TimeLogStatus.VERIFIED
    
    @property
    def has_gps(self) -> bool:
        """Check if time log has GPS coordinates"""
        return self.latitude is not None and self.longitude is not None
    
    @property
    def is_adjustment(self) -> bool:
        """Check if time log is a manual adjustment"""
        return self.log_type == TimeLogType.MANUAL_ADJUSTMENT 