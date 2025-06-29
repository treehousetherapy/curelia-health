"""
Shift model for scheduling caregiver shifts
Manages shift scheduling and recurring patterns
"""

import enum
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Enum, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from .base import BaseModel


class ShiftStatus(enum.Enum):
    """Status of a shift"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class RecurrencePattern(enum.Enum):
    """Recurrence pattern for recurring shifts"""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Shift(BaseModel):
    """
    Shift model for scheduling caregiver visits
    Used for planning, EVV verification, and payroll calculations
    """
    __tablename__ = "shifts"
    
    # Relationships
    caregiver_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("caregivers.id"), 
        nullable=False,
        index=True,
        comment="Reference to assigned caregiver"
    )
    
    client_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("clients.id"), 
        nullable=False,
        index=True,
        comment="Reference to client receiving service"
    )
    
    # Schedule details
    start_time = Column(
        DateTime, 
        nullable=False,
        index=True,
        comment="Scheduled start time"
    )
    
    end_time = Column(
        DateTime, 
        nullable=False,
        index=True,
        comment="Scheduled end time"
    )
    
    # Ensure end_time is after start_time
    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_shift_times'),
    )
    
    status = Column(
        Enum(ShiftStatus),
        nullable=False,
        default=ShiftStatus.SCHEDULED,
        index=True,
        comment="Current status of the shift"
    )
    
    # Service details
    service_type = Column(
        String(100),
        nullable=False,
        comment="Type of service to be provided"
    )
    
    service_codes = Column(
        JSONB,
        nullable=True,
        comment="Service codes for billing/payroll"
    )
    
    # Location
    location_type = Column(
        String(50),
        nullable=False,
        default="client_home",
        comment="Where service is provided (client_home, facility, etc.)"
    )
    
    address = Column(
        String(255),
        nullable=True,
        comment="Service location address (if not client's home address)"
    )
    
    # Recurrence (for recurring shifts)
    is_recurring = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this shift is part of a recurring pattern"
    )
    
    recurrence_pattern = Column(
        Enum(RecurrencePattern),
        nullable=True,
        comment="Pattern of recurrence"
    )
    
    recurrence_days = Column(
        ARRAY(Integer),
        nullable=True,
        comment="Days of week for recurrence (0=Monday, 6=Sunday)"
    )
    
    recurrence_end_date = Column(
        DateTime,
        nullable=True,
        comment="When the recurrence ends (null for indefinite)"
    )
    
    parent_shift_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("shifts.id"), 
        nullable=True,
        comment="Reference to parent shift for recurring instances"
    )
    
    # Additional details
    notes = Column(
        Text,
        nullable=True,
        comment="Notes about the shift"
    )
    
    tasks = Column(
        JSONB,
        nullable=True,
        comment="Tasks to be performed during shift"
    )
    
    # Verification and completion
    requires_evv = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this shift requires EVV verification"
    )
    
    clock_in_tolerance_minutes = Column(
        Integer,
        nullable=False,
        default=15,
        comment="Minutes early/late allowed for clock-in"
    )
    
    clock_out_tolerance_minutes = Column(
        Integer,
        nullable=False,
        default=15,
        comment="Minutes early/late allowed for clock-out"
    )
    
    # Relationships
    caregiver = relationship("Caregiver", back_populates="shifts")
    client = relationship("Client", back_populates="shifts")
    timelogs = relationship("TimeLog", back_populates="shift")
    child_shifts = relationship("Shift", 
                               backref=relationship("parent", remote_side="Shift.id"),
                               foreign_keys=[parent_shift_id])
    
    def __repr__(self):
        return f"<Shift {self.id} for {self.client_id} with {self.caregiver_id} at {self.start_time}>"
    
    @property
    def duration_minutes(self) -> int:
        """Calculate scheduled duration in minutes"""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
    
    @property
    def is_active(self) -> bool:
        """Check if shift is currently active"""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time and self.status == ShiftStatus.IN_PROGRESS
    
    @property
    def is_late(self) -> bool:
        """Check if caregiver is late for shift"""
        now = datetime.utcnow()
        return now > self.start_time and self.status == ShiftStatus.SCHEDULED
    
    @property
    def has_clock_in(self) -> bool:
        """Check if shift has a clock-in record"""
        return any(log.log_type == "CLOCK_IN" for log in self.timelogs)
    
    @property
    def has_clock_out(self) -> bool:
        """Check if shift has a clock-out record"""
        return any(log.log_type == "CLOCK_OUT" for log in self.timelogs) 