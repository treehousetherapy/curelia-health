"""
Patient API endpoints for CRUD operations
HIPAA-compliant patient data management
"""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_

from app.db.session import get_db
from app.models.patient import Patient, PatientContact, PatientStatus
from app.models.audit import AuditLog, AuditAction
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
    PatientContactCreate,
    PatientContactUpdate,
    PatientContactResponse
)
from app.core.security import get_current_user, validate_patient_access
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    request: Request,
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new patient record
    
    Requires staff or admin privileges
    """
    # Check permissions - only staff or admin can create patients
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]:
        # Log unauthorized access attempt
        audit_log = AuditLog(
            user_id=current_user.id,
            action=AuditAction.ACCESS_DENIED,
            resource_type="Patient",
            description=f"Unauthorized attempt to create patient by {current_user.email}",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(audit_log)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create patients"
        )
    
    # Create new patient
    patient = Patient(**patient_data.dict())
    
    # Set audit fields
    patient.created_by_id = current_user.id
    patient.updated_by_id = current_user.id
    
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    
    # Log patient creation
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.CREATE,
        resource_type="Patient",
        resource_id=patient.id,
        description=f"Created patient record for {patient.full_name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    await db.commit()
    
    return patient


@router.get("/", response_model=List[PatientListResponse])
async def list_patients(
    request: Request,
    search: Optional[str] = Query(None, description="Search by name or MRN"),
    status: Optional[PatientStatus] = Query(None, description="Filter by patient status"),
    high_risk: Optional[bool] = Query(None, description="Filter by high risk flag"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max number of records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List patients with optional filtering
    
    Results are paginated and can be filtered by search term, status, and risk level
    """
    # Base query
    query = select(Patient)
    
    # Apply filters
    filters = []
    
    if search:
        search_term = f"%{search}%"
        filters.append(
            or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                Patient.medical_record_number.ilike(search_term)
            )
        )
    
    if status:
        filters.append(Patient.status == status)
    
    if high_risk is not None:
        filters.append(Patient.is_high_risk == high_risk)
    
    # Apply all filters
    if filters:
        query = query.where(and_(*filters))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    patients = result.scalars().all()
    
    # Log access
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.READ,
        resource_type="Patient",
        description=f"Listed patients with filters: search={search}, status={status}, high_risk={high_risk}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    await db.commit()
    
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    request: Request,
    patient_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
    _: tuple = Depends(validate_patient_access)  # Validates access and logs it
):
    """
    Get a specific patient by ID
    
    Access is validated based on user role and relationship to patient
    """
    # Query patient
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    request: Request,
    patient_id: uuid.UUID,
    patient_data: PatientUpdate,
    current_user: User,
    db: AsyncSession,
    _: tuple = Depends(validate_patient_access)  # Validates access and logs it
):
    """
    Update a patient record
    
    Access is validated based on user role and relationship to patient
    """
    # Query patient
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Track changes for audit
    old_values = patient.to_dict()
    
    # Update patient with new data, skipping None values
    update_data = patient_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(patient, key, value)
    
    # Update audit fields
    patient.updated_by_id = current_user.id
    
    await db.commit()
    await db.refresh(patient)
    
    # Log update with changed fields
    new_values = patient.to_dict()
    changed_fields = {k: new_values[k] for k in new_values if k in old_values and old_values[k] != new_values[k]}
    
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        resource_type="Patient",
        resource_id=patient.id,
        description=f"Updated patient record for {patient.full_name}",
        old_values=old_values,
        new_values=changed_fields,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    await db.commit()
    
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    request: Request,
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a patient record
    
    Only administrators can delete patient records
    """
    # Check permissions - only admin can delete patients
    if current_user.role != UserRole.ADMIN:
        # Log unauthorized access attempt
        audit_log = AuditLog(
            user_id=current_user.id,
            action=AuditAction.ACCESS_DENIED,
            resource_type="Patient",
            resource_id=patient_id,
            description=f"Unauthorized attempt to delete patient by {current_user.email}",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(audit_log)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete patient records"
        )
    
    # Query patient
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Soft delete
    patient.soft_delete(current_user.id)
    await db.commit()
    
    # Log deletion
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.DELETE,
        resource_type="Patient",
        resource_id=patient.id,
        description=f"Soft deleted patient record for {patient.full_name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    await db.commit()
    
    return None


# Patient Contact Endpoints

@router.post("/{patient_id}/contacts", response_model=PatientContactResponse, status_code=status.HTTP_201_CREATED)
async def create_patient_contact(
    request: Request,
    patient_id: uuid.UUID,
    contact_data: PatientContactCreate,
    current_user: User,
    db: AsyncSession,
    _: tuple = Depends(validate_patient_access)  # Validates access and logs it
):
    """
    Create a new contact for a patient
    
    Access is validated based on user role and relationship to patient
    """
    # Verify patient exists
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Create contact
    contact = PatientContact(**contact_data.dict())
    
    # Set audit fields
    contact.created_by_id = current_user.id
    contact.updated_by_id = current_user.id
    
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    
    # Log contact creation
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.CREATE,
        resource_type="PatientContact",
        resource_id=contact.id,
        description=f"Created contact {contact.full_name} for patient {patient.full_name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    await db.commit()
    
    return contact


@router.get("/{patient_id}/contacts", response_model=List[PatientContactResponse])
async def list_patient_contacts(
    request: Request,
    patient_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
    _: tuple = Depends(validate_patient_access)  # Validates access and logs it
):
    """
    List all contacts for a patient
    
    Access is validated based on user role and relationship to patient
    """
    # Query contacts
    result = await db.execute(
        select(PatientContact)
        .filter(PatientContact.patient_id == patient_id)
        .order_by(PatientContact.contact_priority)
    )
    contacts = result.scalars().all()
    
    # Log access
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.READ,
        resource_type="PatientContact",
        resource_id=patient_id,
        description=f"Listed contacts for patient ID {patient_id}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    await db.commit()
    
    return contacts


@router.get("/{patient_id}/contacts/{contact_id}", response_model=PatientContactResponse)
async def get_patient_contact(
    request: Request,
    patient_id: uuid.UUID,
    contact_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
    _: tuple = Depends(validate_patient_access)  # Validates access and logs it
):
    """
    Get a specific contact for a patient
    
    Access is validated based on user role and relationship to patient
    """
    # Query contact
    result = await db.execute(
        select(PatientContact)
        .filter(PatientContact.id == contact_id, PatientContact.patient_id == patient_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Log access
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.READ,
        resource_type="PatientContact",
        resource_id=contact.id,
        description=f"Retrieved contact {contact.full_name} for patient ID {patient_id}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    await db.commit()
    
    return contact


@router.put("/{patient_id}/contacts/{contact_id}", response_model=PatientContactResponse)
async def update_patient_contact(
    request: Request,
    patient_id: uuid.UUID,
    contact_id: uuid.UUID,
    contact_data: PatientContactUpdate,
    current_user: User,
    db: AsyncSession,
    _: tuple = Depends(validate_patient_access)  # Validates access and logs it
):
    """
    Update a specific contact for a patient
    
    Access is validated based on user role and relationship to patient
    """
    # Query contact
    result = await db.execute(
        select(PatientContact)
        .filter(PatientContact.id == contact_id, PatientContact.patient_id == patient_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Track changes for audit
    old_values = contact.to_dict()
    
    # Update contact with new data, skipping None values
    update_data = contact_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(contact, key, value)
    
    # Update audit fields
    contact.updated_by_id = current_user.id
    
    await db.commit()
    await db.refresh(contact)
    
    # Log update with changed fields
    new_values = contact.to_dict()
    changed_fields = {k: new_values[k] for k in new_values if k in old_values and old_values[k] != new_values[k]}
    
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        resource_type="PatientContact",
        resource_id=contact.id,
        description=f"Updated contact {contact.full_name} for patient ID {patient_id}",
        old_values=old_values,
        new_values=changed_fields,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    await db.commit()
    
    return contact


@router.delete("/{patient_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient_contact(
    request: Request,
    patient_id: uuid.UUID,
    contact_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
    _: tuple = Depends(validate_patient_access)  # Validates access and logs it
):
    """
    Delete a specific contact for a patient
    
    Access is validated based on user role and relationship to patient
    """
    # Query contact
    result = await db.execute(
        select(PatientContact)
        .filter(PatientContact.id == contact_id, PatientContact.patient_id == patient_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Soft delete
    contact.soft_delete(current_user.id)
    await db.commit()
    
    # Log deletion
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.DELETE,
        resource_type="PatientContact",
        resource_id=contact.id,
        description=f"Deleted contact {contact.full_name} for patient ID {patient_id}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    await db.commit()
    
    return None
