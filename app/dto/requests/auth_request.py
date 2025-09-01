from pydantic import BaseModel, Field

class LoginTestRequest(BaseModel):
    """Request DTO for test login"""
    customer_id: int = Field(..., gt=0, description="Customer ID must be positive")

class RefreshTokenRequest(BaseModel):
    """Request DTO for refreshing token"""
    refresh_token: str = Field(..., description="Refresh token")
