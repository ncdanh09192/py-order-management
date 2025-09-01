from fastapi import APIRouter, HTTPException, Depends
from app.services.auth_service import AuthService
from app.dto.requests.auth_request import LoginTestRequest, RefreshTokenRequest
from app.dto.responses.auth_response import LoginTestResponse, TokenResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login-test", response_model=LoginTestResponse)
async def login_test(request: LoginTestRequest):
    """
    Test login endpoint that returns JWT tokens.
    
    In production, this would validate credentials against database.
    For testing purposes, it accepts any positive customer_id.
    """
    try:
        auth_service = AuthService()
        return await auth_service.login_test(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Login test error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    
    This endpoint allows users to get a new access token
    without re-authenticating.
    """
    try:
        auth_service = AuthService()
        return await auth_service.refresh_token(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
