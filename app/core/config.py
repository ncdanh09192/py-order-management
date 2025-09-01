from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    
    # Redis Configuration
    REDIS_URL: str = Field(..., description="Redis connection URL")
    
    # JWT Configuration
    SECRET_KEY: str = Field(..., description="JWT secret key")
    REFRESH_SECRET_KEY: str = Field(..., description="JWT refresh secret key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")
    
    # Event System Configuration
    EVENT_SYSTEM: str = Field(default="local", description="Event system type: local or sqs")
    
    # SQS Configuration (for production)
    SQS_QUEUE_URL: Optional[str] = Field(default=None, description="SQS queue URL")
    AWS_REGION: str = Field(default="us-east-1", description="AWS region")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
