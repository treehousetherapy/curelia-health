"""
Application configuration settings
Loads settings from environment variables
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database settings
    DATABASE_URL: PostgresDsn
    SQL_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Security settings
    ALGORITHM: str = "HS256"
    VERIFY_EMAIL: bool = True
    VERIFY_PHONE: bool = True
    PASSWORD_MIN_LENGTH: int = 8
    
    # EVV settings
    EVV_GEOFENCE_RADIUS_METERS: float = 100.0  # Default geofence radius
    EVV_REQUIRE_PHOTO: bool = False
    EVV_REQUIRE_SIGNATURE: bool = True
    
    # Storage settings
    STORAGE_BACKEND: str = "s3"  # s3, gcs, azure, or local
    STORAGE_BUCKET_NAME: str = ""
    STORAGE_ACCESS_KEY: Optional[str] = None
    STORAGE_SECRET_KEY: Optional[str] = None
    STORAGE_REGION: Optional[str] = None
    STORAGE_ENDPOINT_URL: Optional[str] = None
    
    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # SMS settings
    SMS_PROVIDER: str = "twilio"  # twilio, sns, etc.
    SMS_ACCOUNT_SID: Optional[str] = None
    SMS_AUTH_TOKEN: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # HIPAA compliance settings
    HIPAA_ENABLE_AUDIT_LOGGING: bool = True
    HIPAA_SESSION_TIMEOUT_MINUTES: int = 30
    HIPAA_REQUIRE_MFA: bool = True
    HIPAA_PASSWORD_EXPIRY_DAYS: int = 90
    
    class Config:
        """Pydantic config"""
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings() 