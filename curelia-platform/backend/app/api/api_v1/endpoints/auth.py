"""
Authentication endpoints for user login, registration, and password management
"""

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import authenticate_user, create_access_token, get_password_hash
from app.config import settings
from app.db.database import get_db
from app.models.audit import AuditAction

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Log failed login attempt
        models.AuditLog.log(
            db,
            action=AuditAction.LOGIN_FAILED,
            description=f"Failed login attempt for {form_data.username}",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    # Log successful login
    models.AuditLog.log(
        db,
        action=AuditAction.LOGIN,
        user_id=user.id,
        description=f"Successful login for {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "full_name": user.full_name,
    }


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
) -> models.User:
    """
    Register a new user
    """
    # Check if user with this email already exists
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    # Create new user
    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role=user_in.role,
        is_active=True,
        is_verified=False,  # Requires email verification
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log user registration
    models.AuditLog.log(
        db,
        action=AuditAction.CREATE,
        user_id=user.id,
        resource_type="User",
        resource_id=user.id,
        description=f"User registration for {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return user


@router.post("/reset-password", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(
    request: Request,
    reset_data: schemas.PasswordResetRequest,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Request a password reset
    """
    user = db.query(models.User).filter(models.User.email == reset_data.email).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If your email is registered, you will receive a password reset link"}
    
    # TODO: Implement password reset email sending
    
    # Log password reset request
    models.AuditLog.log(
        db,
        action=AuditAction.PASSWORD_RESET,
        user_id=user.id,
        resource_type="User",
        resource_id=user.id,
        description=f"Password reset requested for {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return {"message": "If your email is registered, you will receive a password reset link"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: Request,
    change_data: schemas.PasswordChange,
    current_user: models.User = Depends(schemas.get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Change user password
    """
    # Verify current password
    if not authenticate_user(db, current_user.email, change_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(change_data.new_password)
    current_user.password_changed_at = models.datetime.utcnow()
    
    db.commit()
    
    # Log password change
    models.AuditLog.log(
        db,
        action=AuditAction.PASSWORD_CHANGED,
        user_id=current_user.id,
        resource_type="User",
        resource_id=current_user.id,
        description=f"Password changed for {current_user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    
    return {"message": "Password changed successfully"} 