from app.core.security import create_access_token, create_refresh_token
from app.dto.requests.auth_request import LoginTestRequest, RefreshTokenRequest
from app.dto.responses.auth_response import LoginTestResponse, TokenResponse
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Service for authentication operations"""
    
    async def login_test(self, request: LoginTestRequest) -> LoginTestResponse:
        """Test login endpoint that returns JWT tokens"""
        try:
            # In production, this would validate credentials against database
            # For now, just validate customer_id is positive
            if request.customer_id <= 0:
                raise ValueError("Invalid customer ID")
            
            # Create tokens with customer_id
            access_token = create_access_token(
                data={"sub": str(request.customer_id), "customer_id": request.customer_id}
            )
            
            refresh_token = create_refresh_token(
                data={"sub": str(request.customer_id), "customer_id": request.customer_id}
            )
            
            logger.info(f"Test login successful for customer {request.customer_id}")
            
            return LoginTestResponse(
                accessToken=access_token,
                refreshToken=refresh_token,
                tokenType="bearer",
                expiresIn=1800,  # 30 minutes in seconds
                customerId=request.customer_id
            )
            
        except Exception as e:
            logger.error(f"Login test failed: {str(e)}")
            raise
    
    async def refresh_token(self, request: RefreshTokenRequest) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            from app.core.security import verify_refresh_token
            
            # Verify refresh token
            payload = verify_refresh_token(request.refresh_token)
            customer_id = payload.get("customer_id")
            
            if not customer_id:
                raise ValueError("Invalid refresh token payload")
            
            # Create new access token
            new_access_token = create_access_token(
                data={"sub": str(customer_id), "customer_id": customer_id}
            )
            
            # Create new refresh token
            new_refresh_token = create_refresh_token(
                data={"sub": str(customer_id), "customer_id": customer_id}
            )
            
            logger.info(f"Token refreshed for customer {customer_id}")
            
            return TokenResponse(
                accessToken=new_access_token,
                refreshToken=new_refresh_token,
                tokenType="bearer",
                expiresIn=1800
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise
