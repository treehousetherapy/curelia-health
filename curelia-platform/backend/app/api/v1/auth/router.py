from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    generate_password_reset_token,
    verify_password_reset_token,
    get_password_hash
)
from app.db.session import get_db
from app.models.user import User
from app.models.audit import AuditLog, AuditAction
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest
)
from app.schemas.token import Token
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Find user by email
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    # Validate user and password
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed login attempt
        if user:
            # Update failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account if too many failed attempts
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.is_locked = True
                
            # Create audit log
            audit_log = AuditLog(
                user_id=user.id,
                action=AuditAction.ACCESS_DENIED,
                resource_type="Authentication",
                description=f"Failed login attempt for user {user.email}"
            )
            db.add(audit_log)
            await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account locked due to too many failed login attempts",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        subject=str(user.id)
    )
    
    # Log successful login
    user.last_login_at = db.func.now()
    user.failed_login_attempts = 0
    
    audit_log = AuditLog(
        user_id=user.id,
        action=AuditAction.LOGIN,
        resource_type="Authentication",
        description=f"User {user.email} logged in successfully"
    )
    db.add(audit_log)
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a new access token from refresh token
    """
    try:
        # Decode refresh token
        payload = decode_token(token_data.refresh_token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Find user in database
        result = await db.execute(select(User).filter(User.id == user_id, User.is_active == True))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )
        
        # Log token refresh
        audit_log = AuditLog(
            user_id=user.id,
            action=AuditAction.LOGIN,
            resource_type="Authentication",
            description=f"User {user.email} refreshed access token"
        )
        db.add(audit_log)
        await db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": token_data.refresh_token,  # Return the same refresh token
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/password-reset", response_model=dict)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Request password reset token (sends email with token)
    """
    # Find user by email
    result = await db.execute(select(User).filter(User.email == reset_data.email))
    user = result.scalar_one_or_none()
    
    # Always return success even if user not found (security)
    if not user:
        return {"message": "If this email exists, a password reset link has been sent"}
    
    # Generate password reset token
    reset_token = generate_password_reset_token(user.email)
    
    # In a real application, send email with token
    # For now, just log it
    print(f"Password reset token for {user.email}: {reset_token}")
    
    # Log password reset request
    audit_log = AuditLog(
        user_id=user.id,
        action=AuditAction.UPDATE,
        resource_type="Authentication",
        description=f"Password reset requested for user {user.email}"
    )
    db.add(audit_log)
    await db.commit()
    
    return {"message": "If this email exists, a password reset link has been sent"}


@router.post("/password-reset-confirm", response_model=dict)
async def confirm_password_reset(
    reset_data: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Reset password using token
    """
    # Verify token and get email
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Find user by email
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.password_changed_at = db.func.now()
    
    # Reset security flags
    user.failed_login_attempts = 0
    user.is_locked = False
    
    # Log password change
    audit_log = AuditLog(
        user_id=user.id,
        action=AuditAction.UPDATE,
        resource_type="Authentication",
        description=f"Password reset completed for user {user.email}"
    )
    db.add(audit_log)
    await db.commit()
    
    return {"message": "Password has been reset successfully"} 