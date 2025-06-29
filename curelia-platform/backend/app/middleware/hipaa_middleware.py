"""
HIPAA compliance middleware
Enforces session timeout and security requirements
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger(__name__)


class HIPAAMiddleware(BaseHTTPMiddleware):
    """
    Middleware for HIPAA compliance
    Enforces session timeout and security requirements
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and enforce HIPAA requirements"""
        # Skip public endpoints
        path = request.url.path
        if self._is_public_endpoint(path):
            return await call_next(request)
        
        # Check session timeout
        if self._is_session_expired(request):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Session expired due to inactivity"},
            )
        
        # Update last activity timestamp
        if hasattr(request.state, "user_id"):
            request.session["last_activity"] = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if the endpoint is public (no auth required)"""
        public_paths = [
            "/health",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            f"{settings.API_V1_STR}/auth/login",
            f"{settings.API_V1_STR}/auth/register",
            f"{settings.API_V1_STR}/auth/reset-password",
        ]
        
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _is_session_expired(self, request: Request) -> bool:
        """Check if the session has expired due to inactivity"""
        # Skip if no user is authenticated
        if not hasattr(request.state, "user_id"):
            return False
        
        # Skip if session tracking is disabled
        if not hasattr(request, "session"):
            return False
        
        # Get last activity time
        last_activity = request.session.get("last_activity", 0)
        
        # Calculate inactivity time
        inactivity_time = time.time() - last_activity
        
        # Check if session has expired
        timeout_seconds = settings.HIPAA_SESSION_TIMEOUT_MINUTES * 60
        return inactivity_time > timeout_seconds 