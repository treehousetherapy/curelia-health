"""
Token schemas for authentication
"""

from typing import Optional
from pydantic import BaseModel, UUID4


class Token(BaseModel):
    """
    Schema for access token response
    """
    access_token: str
    token_type: str
    user_id: str
    email: str
    role: str
    full_name: str


class TokenPayload(BaseModel):
    """
    Schema for JWT token payload
    """
    sub: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None 