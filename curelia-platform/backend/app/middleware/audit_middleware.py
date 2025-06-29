"""
Audit middleware for HIPAA-compliant logging
Records all API requests and responses for audit trail
"""

import logging
import time
import uuid
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings
from app.db.database import SessionLocal
from app.models.audit import AuditLog, AuditAction

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for HIPAA-compliant audit logging
    Records all API requests and responses
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log for audit trail"""
        # Skip audit logging if disabled
        if not settings.HIPAA_ENABLE_AUDIT_LOGGING:
            return await call_next(request)
        
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Skip health check endpoints from detailed logging
        is_health_check = path.endswith("/health")
        
        # Get user ID if authenticated
        user_id = getattr(request.state, "user_id", None)
        
        # Process the request
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add headers to response
            response.headers["X-Request-ID"] = request_id
            
            # Log the request (excluding health checks)
            if not is_health_check and settings.HIPAA_ENABLE_AUDIT_LOGGING:
                try:
                    # Create database session
                    db = SessionLocal()
                    
                    # Determine action type
                    if method == "GET":
                        action = AuditAction.ACCESS
                    elif method == "POST":
                        action = AuditAction.CREATE
                    elif method in ("PUT", "PATCH"):
                        action = AuditAction.UPDATE
                    elif method == "DELETE":
                        action = AuditAction.DELETE
                    else:
                        action = AuditAction.ACCESS
                    
                    # Create audit log entry
                    AuditLog.log(
                        db,
                        action=action,
                        user_id=user_id,
                        description=f"{method} {path}",
                        ip_address=client_host,
                        user_agent=user_agent,
                        request_id=request_id,
                        metadata={
                            "method": method,
                            "path": path,
                            "query_params": query_params,
                            "status_code": status_code,
                            "duration": round(process_time, 4),
                        },
                    )
                    
                    db.commit()
                except Exception as e:
                    logger.error(f"Error creating audit log: {e}")
                finally:
                    db.close()
            
            return response
            
        except Exception as e:
            # Log exceptions
            logger.exception(f"Unhandled exception in request: {e}")
            
            # Re-raise the exception to be handled by FastAPI
            raise 