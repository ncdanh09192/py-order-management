from pydantic import BaseModel, Field

class LoginTestResponse(BaseModel):
    """Response DTO for test login"""
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    token_type: str = Field(..., alias="tokenType")
    expires_in: int = Field(..., alias="expiresIn")
    customer_id: int = Field(..., alias="customerId")
    
    class Config:
        allow_population_by_field_name = True

class TokenResponse(BaseModel):
    """Response DTO for token operations"""
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    token_type: str = Field(..., alias="tokenType")
    expires_in: int = Field(..., alias="expiresIn")
    
    class Config:
        allow_population_by_field_name = True
