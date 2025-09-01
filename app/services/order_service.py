from typing import Dict, List, Optional
from decimal import Decimal
from app.core.database import get_database
from app.events.event_bus import EventBus
from app.events.order_events import OrderCreatedEvent, OrderUpdatedEvent, OrderDeletedEvent
from app.dto.requests.order_request import CreateOrderRequest, UpdateOrderRequest
from app.dto.responses.order_response import OrderResponse, OrderLineResponse, OrderListResponse
from app.cache.redis_client import redis_client
import json
import logging

logger = logging.getLogger(__name__)

class OrderService:
    """Service for order operations"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    async def create_order(self, order_data: CreateOrderRequest, customer_id: int) -> Dict:
        """Create a new order with lines"""
        try:
            db = await get_database()
            
            # Calculate total amount
            total_amount = self._calculate_total_amount(order_data.lines)
            
            # Create order header
            order_header = await db.orderheader.create(
                data={
                    "customerId": customer_id,
                    "orderDate": order_data.order_date,
                    "status": order_data.status,
                    "totalAmount": total_amount
                }
            )
            
            # Create order lines
            order_lines = []
            for line_data in order_data.lines:
                line = await db.orderline.create(
                    data={
                        "orderId": order_header.id,
                        "productId": line_data.product_id,
                        "quantity": line_data.quantity,
                        "unitPrice": line_data.unit_price
                    }
                )
                order_lines.append(line)
            
            # Prepare response data
            response_data = {
                "id": order_header.id,
                "customerId": order_header.customerId,
                "orderDate": order_header.orderDate,
                "status": order_header.status,
                "totalAmount": order_header.totalAmount,
                "createdAt": order_header.createdAt,
                "updatedAt": order_header.updatedAt,
                "lines": [
                    {
                        "id": line.id,
                        "productId": line.productId,
                        "quantity": line.quantity,
                        "unitPrice": line.unitPrice,
                        "createdAt": line.createdAt
                    }
                    for line in order_lines
                ]
            }
            
            # Publish event
            event = OrderCreatedEvent(response_data)
            await self.event_bus.publish(event)
            
            logger.info(f"Order {order_header.id} created successfully")
            return response_data
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise
    
    async def get_order_by_id(self, order_id: int, customer_id: int) -> Optional[Dict]:
        """Get order by ID with cache first strategy"""
        try:
            # Try to get from cache first
            cache_key = f"order:{order_id}"
            cached_order = await redis_client.get(cache_key)
            
            if cached_order:
                order_data = json.loads(cached_order)
                # Verify ownership
                if order_data.get("customerId") == customer_id:
                    logger.info(f"Order {order_id} retrieved from cache")
                    return order_data
            
            # If not in cache or ownership mismatch, get from database
            db = await get_database()
            
            order_header = await db.orderheader.find_first(
                where={"id": order_id, "customerId": customer_id},
                include={"lines": True}
            )
            
            if not order_header:
                return None
            
            # Prepare response data
            response_data = {
                "id": order_header.id,
                "customer_id": order_header.customerId,
                "order_date": order_header.orderDate,
                "status": order_header.status,
                "total_amount": order_header.totalAmount,
                "created_at": order_header.createdAt,
                "updated_at": order_header.updatedAt,
                "lines": [
                    {
                        "id": line.id,
                        "product_id": line.productId,
                        "quantity": line.quantity,
                        "unit_price": line.unitPrice,
                        "created_at": line.createdAt
                    }
                    for line in order_header.lines
                ]
            }
            
            # Cache the order
            await redis_client.set(cache_key, json.dumps(response_data), expire=3600)
            
            logger.info(f"Order {order_id} retrieved from database and cached")
            return response_data
            
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {str(e)}")
            raise
    
    async def update_order(self, order_id: int, update_data: UpdateOrderRequest, customer_id: int) -> Optional[Dict]:
        """Update order status"""
        try:
            db = await get_database()
            
            # Get current order
            current_order = await db.orderheader.find_first(
                where={"id": order_id, "customerId": customer_id}
            )
            
            if not current_order:
                return None
            
            # Store old data for event
            old_data = {
                "id": current_order.id,
                "customerId": current_order.customerId,
                "orderDate": current_order.orderDate,
                "status": current_order.status,
                "totalAmount": current_order.totalAmount,
                "createdAt": current_order.createdAt,
                "updatedAt": current_order.updatedAt
            }
            
            # Update order
            updated_order = await db.orderheader.update(
                where={"id": order_id},
                data={"status": update_data.status}
            )
            
            # Get updated order with lines
            updated_order_with_lines = await db.orderheader.find_first(
                where={"id": order_id},
                include={"lines": True}
            )
            
            # Prepare response data
            response_data = {
                "id": updated_order_with_lines.id,
                "customerId": updated_order_with_lines.customerId,
                "orderDate": updated_order_with_lines.orderDate,
                "status": updated_order_with_lines.status,
                "totalAmount": updated_order_with_lines.totalAmount,
                "createdAt": updated_order_with_lines.createdAt,
                "updatedAt": updated_order_with_lines.updatedAt,
                "lines": [
                    {
                        "id": line.id,
                        "productId": line.productId,
                        "quantity": line.quantity,
                        "unitPrice": line.unitPrice,
                        "createdAt": line.createdAt
                    }
                    for line in updated_order_with_lines.lines
                ]
            }
            
            # Publish event
            event = OrderUpdatedEvent(order_id, old_data, response_data)
            await self.event_bus.publish(event)
            
            logger.info(f"Order {order_id} updated successfully")
            return response_data
            
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {str(e)}")
            raise
    
    async def delete_order(self, order_id: int, customer_id: int) -> bool:
        """Delete order"""
        try:
            db = await get_database()
            
            # Get order data before deletion for event
            order_data = await db.orderheader.find_first(
                where={"id": order_id, "customerId": customer_id},
                include={"lines": True}
            )
            
            if not order_data:
                return False
            
            # Store order data for event
            order_data_dict = {
                "id": order_data.id,
                "customerId": order_data.customerId,
                "orderDate": order_data.orderDate,
                "status": order_data.status,
                "totalAmount": order_data.totalAmount,
                "createdAt": order_data.createdAt,
                "updatedAt": order_data.updatedAt,
                "lines": [
                    {
                        "id": line.id,
                        "productId": line.productId,
                        "quantity": line.quantity,
                        "unitPrice": line.unitPrice,
                        "createdAt": line.createdAt
                    }
                    for line in order_data.lines
                ]
            }
            
            # Delete order (cascade will delete lines)
            await db.orderheader.delete(where={"id": order_id})
            
            # Publish event
            event = OrderDeletedEvent(order_id, order_data_dict)
            await self.event_bus.publish(event)
            
            logger.info(f"Order {order_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting order {order_id}: {str(e)}")
            raise
    
    async def list_orders(self, customer_id: int, page: int = 1, size: int = 10) -> OrderListResponse:
        """List orders with pagination"""
        try:
            db = await get_database()
            
            # Calculate skip
            skip = (page - 1) * size
            
            # Get total count
            total = await db.orderheader.count(where={"customerId": customer_id})
            
            # Get orders
            orders = await db.orderheader.find_many(
                where={"customerId": customer_id},
                include={"lines": True},
                skip=skip,
                take=size,
                order={"createdAt": "desc"}
            )
            
            # Prepare response
            order_responses = []
            for order in orders:
                order_response = {
                    "id": order.id,
                    "customerId": order.customerId,
                    "orderDate": order.orderDate,
                    "status": order.status,
                    "totalAmount": order.totalAmount,
                    "createdAt": order.createdAt,
                    "updatedAt": order.updatedAt,
                    "lines": [
                        {
                            "id": line.id,
                            "productId": line.productId,
                            "quantity": line.quantity,
                            "unitPrice": line.unitPrice,
                            "createdAt": line.createdAt
                        }
                        for line in order.lines
                    ]
                }
                order_responses.append(order_response)
            
            return OrderListResponse(
                orders=order_responses,
                total=total,
                page=page,
                size=size,
                has_next=page * size < total,
                has_prev=page > 1
            )
            
        except Exception as e:
            logger.error(f"Error listing orders: {str(e)}")
            raise
    
    def _calculate_total_amount(self, lines: List) -> Decimal:
        """Calculate total amount from order lines"""
        total = Decimal('0')
        for line in lines:
            total += line.unit_price * line.quantity
        return total
