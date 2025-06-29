"""
Patient schemas for request validation and response serialization
HIPAA-compliant data handling
"""

from datetime import date
from typing import Optional, List, Dict, Any
import uuid

from pydantic import BaseModel, EmailStr, Field, validator, root_validator

from app.models.patient import PatientStatus, Gender, MaritalStatus


# Base schema with common fields
class PatientBase(BaseModel):
    """Base patient schema with common fields"""
    first_name: str = Field(..., min_length=1, max_length=100, example="John")
    last_name: str = Field(..., min_length=1, max_length=100, example="Doe")
    middle_name: Optional[str] = Field(None, max_length=100, example="Robert")
    date_of_birth: date = Field(..., example="1980-01-01")
    gender: Gender = Field(..., example=Gender.MALE)
    
    # Contact information
    phone_primary: Optional[str] = Field(None, max_length=20, example="555-123-4567")
    phone_secondary: Optional[str] = Field(None, max_length=20, example="555-987-6543")
    email: Optional[EmailStr] = Field(None, example="patient@example.com")
    
    # Address
    address_line1: Optional[str] = Field(None, max_length=255, example="123 Main St")
    address_line2: Optional[str] = Field(None, max_length=255, example="Apt 4B")
    city: Optional[str] = Field(None, max_length=100, example="Springfield")
    state: Optional[str] = Field(None, max_length=50, example="IL")
    zip_code: Optional[str] = Field(None, max_length=20, example="62704")
    country: Optional[str] = Field("United States", max_length=100)
    
    # Additional demographic information
    ssn_last_four: Optional[str] = Field(None, min_length=4, max_length=4, example="1234")
    marital_status: Optional[MaritalStatus] = Field(None, example=MaritalStatus.SINGLE)
    
    # Medical information
    medical_record_number: Optional[str] = Field(None, max_length=50, example="MRN12345")
    primary_diagnosis: Optional[str] = Field(None, example="Hypertension")
    secondary_diagnoses: Optional[List[str]] = Field(None, example=["Diabetes Type 2", "Asthma"])
    allergies: Optional[List[Dict[str, str]]] = Field(None, example=[
        {"allergen": "Penicillin", "reaction": "Rash", "severity": "Moderate"},
        {"allergen": "Peanuts", "reaction": "Anaphylaxis", "severity": "Severe"}
    ])
    medications: Optional[List[Dict[str, Any]]] = Field(None, example=[
        {"name": "Lisinopril", "dosage": "10mg", "frequency": "Daily", "route": "Oral"},
        {"name": "Metformin", "dosage": "500mg", "frequency": "Twice daily", "route": "Oral"}
    ])
    medical_history: Optional[str] = Field(None, example="Patient has history of...")
    
    # Care information
    care_level: Optional[str] = Field(None, max_length=50, example="Moderate")
    care_plan: Optional[str] = Field(None, example="Weekly home visits...")
    mobility_status: Optional[str] = Field(None, max_length=100, example="Ambulatory with cane")
    dietary_restrictions: Optional[List[str]] = Field(None, example=["Low sodium", "Diabetic"])
    
    # Insurance information
    insurance_provider: Optional[str] = Field(None, max_length=200, example="Blue Cross Blue Shield")
    insurance_policy_number: Optional[str] = Field(None, max_length=100, example="XYZ123456789")
    insurance_group_number: Optional[str] = Field(None, max_length=100, example="GRP987654")
    secondary_insurance_provider: Optional[str] = Field(None, max_length=200)
    secondary_insurance_policy_number: Optional[str] = Field(None, max_length=100)
    
    # Status and flags
    status: PatientStatus = Field(PatientStatus.ACTIVE, example=PatientStatus.ACTIVE)
    is_high_risk: bool = Field(False, example=False)
    requires_special_care: bool = Field(False, example=False)
    
    # Admission/discharge
    admission_date: Optional[date] = Field(None, example="2023-01-15")
    discharge_date: Optional[date] = Field(None, example=None)
    discharge_reason: Optional[str] = Field(None, example=None)
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        """Validate that birth date is not in the future"""
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v
    
    @validator('discharge_date')
    def validate_discharge_date(cls, v, values):
        """Validate that discharge date is after admission date"""
        if v and 'admission_date' in values and values['admission_date'] and v < values['admission_date']:
            raise ValueError("Discharge date must be after admission date")
        return v


# Schema for creating a new patient
class PatientCreate(PatientBase):
    """Schema for creating a new patient"""
    # All fields inherited from PatientBase
    pass


# Schema for updating an existing patient
class PatientUpdate(BaseModel):
    """Schema for updating an existing patient"""
    # All fields are optional for updates
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    
    # Contact information
    phone_primary: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    
    # Address
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    # Additional demographic information
    ssn_last_four: Optional[str] = Field(None, min_length=4, max_length=4)
    marital_status: Optional[MaritalStatus] = None
    
    # Medical information
    medical_record_number: Optional[str] = Field(None, max_length=50)
    primary_diagnosis: Optional[str] = None
    secondary_diagnoses: Optional[List[str]] = None
    allergies: Optional[List[Dict[str, str]]] = None
    medications: Optional[List[Dict[str, Any]]] = None
    medical_history: Optional[str] = None
    
    # Care information
    care_level: Optional[str] = Field(None, max_length=50)
    care_plan: Optional[str] = None
    mobility_status: Optional[str] = Field(None, max_length=100)
    dietary_restrictions: Optional[List[str]] = None
    
    # Insurance information
    insurance_provider: Optional[str] = Field(None, max_length=200)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_group_number: Optional[str] = Field(None, max_length=100)
    secondary_insurance_provider: Optional[str] = Field(None, max_length=200)
    secondary_insurance_policy_number: Optional[str] = Field(None, max_length=100)
    
    # Status and flags
    status: Optional[PatientStatus] = None
    is_high_risk: Optional[bool] = None
    requires_special_care: Optional[bool] = None
    
    # Admission/discharge
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None
    discharge_reason: Optional[str] = None
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        """Validate that birth date is not in the future"""
        if v and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v
    
    @validator('discharge_date')
    def validate_discharge_date(cls, v, values):
        """Validate that discharge date is after admission date"""
        if v and 'admission_date' in values and values['admission_date'] and v < values['admission_date']:
            raise ValueError("Discharge date must be after admission date")
        return v


# Schema for patient response
class PatientResponse(PatientBase):
    """Schema for patient response"""
    id: uuid.UUID
    created_at: date
    updated_at: date
    
    # Computed fields
    age: Optional[int] = None
    full_name: str
    full_address: Optional[str] = None
    
    class Config:
        orm_mode = True


# Schema for patient list response (with fewer fields)
class PatientListResponse(BaseModel):
    """Schema for patient list response with minimal fields"""
    id: uuid.UUID
    full_name: str
    date_of_birth: date
    age: Optional[int] = None
    medical_record_number: Optional[str] = None
    status: PatientStatus
    is_high_risk: bool
    primary_diagnosis: Optional[str] = None
    
    class Config:
        orm_mode = True


# Schema for patient contact
class PatientContactBase(BaseModel):
    """Base schema for patient contact"""
    first_name: str = Field(..., min_length=1, max_length=100, example="Jane")
    last_name: str = Field(..., min_length=1, max_length=100, example="Smith")
    relationship: str = Field(..., min_length=1, max_length=50, example="Spouse")
    phone_primary: str = Field(..., min_length=7, max_length=20, example="555-123-4567")
    phone_secondary: Optional[str] = Field(None, max_length=20, example="555-987-6543")
    email: Optional[EmailStr] = Field(None, example="contact@example.com")
    
    # Address (optional)
    address_line1: Optional[str] = Field(None, max_length=255, example="123 Main St")
    address_line2: Optional[str] = Field(None, max_length=255, example="Apt 4B")
    city: Optional[str] = Field(None, max_length=100, example="Springfield")
    state: Optional[str] = Field(None, max_length=50, example="IL")
    zip_code: Optional[str] = Field(None, max_length=20, example="62704")
    
    # Contact preferences
    is_emergency_contact: bool = Field(False, example=True)
    is_authorized_contact: bool = Field(False, example=True)
    contact_priority: int = Field(1, ge=1, le=10, example=1)


# Schema for creating a new patient contact
class PatientContactCreate(PatientContactBase):
    """Schema for creating a new patient contact"""
    patient_id: uuid.UUID


# Schema for updating an existing patient contact
class PatientContactUpdate(BaseModel):
    """Schema for updating an existing patient contact"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    relationship: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_primary: Optional[str] = Field(None, min_length=7, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    
    # Address (optional)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    
    # Contact preferences
    is_emergency_contact: Optional[bool] = None
    is_authorized_contact: Optional[bool] = None
    contact_priority: Optional[int] = Field(None, ge=1, le=10)


# Schema for patient contact response
class PatientContactResponse(PatientContactBase):
    """Schema for patient contact response"""
    id: uuid.UUID
    patient_id: uuid.UUID
    created_at: date
    updated_at: date
    full_name: str
    
    class Config:
        orm_mode = True 