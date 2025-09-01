from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_access_token
from app.core.database import get_database
from app.models.order_header import OrderHeader
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and validate JWT token, return user payload"""
    token = credentials.credentials
    payload = verify_access_token(token)
    return payload

async def check_order_ownership(order_id: int, current_user: dict = Depends(get_current_user)) -> bool:
    """Verify ownership of an order. Returns True if authorized, raises HTTPException if not."""
    try:
        db = await get_database()
        
        # Get order from database
        order = await db.orderheader.find_first(
            where={"id": order_id}
        )
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check ownership
        if order.customerId != current_user["customer_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this order"
            )

        return True
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking order ownership: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def get_current_customer_id(current_user: dict = Depends(get_current_user)) -> int:
    """Get current customer ID from token"""
    return current_user["customer_id"]
