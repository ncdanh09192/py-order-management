from fastapi import APIRouter, HTTPException, Depends, Query
from app.services.order_service import OrderService
from app.dto.requests.order_request import CreateOrderRequest, UpdateOrderRequest
from app.dto.responses.order_response import OrderResponse, OrderListResponse
from app.core.auth import get_current_customer_id, check_order_ownership
from app.events.event_bus import EventBus
from app.events.handlers.cache_handler import CacheHandler
from app.events.handlers.history_handler import HistoryHandler
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])

# Initialize event bus and handlers
event_bus = EventBus()
cache_handler = CacheHandler()
history_handler = HistoryHandler()

# Register handlers
event_bus.register_handlers([cache_handler, history_handler])

# Initialize order service
order_service = OrderService(event_bus)

@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: CreateOrderRequest,
    customer_id: int = Depends(get_current_customer_id)
):
    """
    Create a new order with multiple order lines.
    
    - **customer_id**: ID of the customer placing the order
    - **order_date**: Date when the order was placed
    - **status**: Current status of the order (pending/shipped/cancelled)
    - **lines**: List of order line items with product details
    """
    try:
        # Validate customer_id matches token
        if order_data.customer_id != customer_id:
            raise HTTPException(
                status_code=403,
                detail="Customer ID mismatch with authentication token"
            )
        
        order = await order_service.create_order(order_data, customer_id)
        return OrderResponse(**order)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    order: dict = Depends(check_order_ownership)
):
    """
    Get order by ID.
    
    Only the order owner can access this endpoint.
    Returns cached data if available, otherwise fetches from database.
    """
    try:
        # Convert order dict to OrderResponse
        return OrderResponse(**order)
        
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    update_data: UpdateOrderRequest,
    customer_id: int = Depends(get_current_customer_id)
):
    """
    Update order status.
    
    Only the order owner can update their orders.
    """
    try:
        updated_order = await order_service.update_order(order_id, update_data, customer_id)
        
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return OrderResponse(**updated_order)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    customer_id: int = Depends(get_current_customer_id)
):
    """
    Delete order.
    
    Only the order owner can delete their orders.
    This will also delete all associated order lines.
    """
    try:
        success = await order_service.delete_order(order_id, customer_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {"message": "Order deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=OrderListResponse)
async def list_orders(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    customer_id: int = Depends(get_current_customer_id)
):
    """
    List orders with pagination.
    
    Returns orders for the authenticated customer only.
    """
    try:
        return await order_service.list_orders(customer_id, page, size)
        
    except Exception as e:
        logger.error(f"Error listing orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
