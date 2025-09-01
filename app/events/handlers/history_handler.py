import json
from app.events.base import EventHandler, Event
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)

class HistoryHandler(EventHandler):
    """Handles order history tracking"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def can_handle(self, event: Event) -> bool:
        """Check if this handler can handle the event"""
        return event.event_type in ["OrderCreated", "OrderUpdated", "OrderDeleted"]
    
    async def handle(self, event: Event) -> None:
        """Handle the event"""
        self.logger.info(f"HistoryHandler processing {event.event_type}")
        
        try:
            if event.event_type == "OrderCreated":
                await self._handle_order_created(event)
            elif event.event_type == "OrderUpdated":
                await self._handle_order_updated(event)
            elif event.event_type == "OrderDeleted":
                await self._handle_order_deleted(event)
                
        except Exception as e:
            self.logger.error(f"HistoryHandler failed: {str(e)}")
            raise
    
    async def _handle_order_created(self, event: Event) -> None:
        """Create history entry for order creation"""
        db = await get_database()
        
        await db.orderhistory.create(
            data={
                "orderId": event.data["id"],
                "action": "CREATED",
                "performedBy": event.data.get("customerId")
            }
        )
        
        self.logger.info(f"Created history entry for order {event.data['id']}")
    
    async def _handle_order_updated(self, event: Event) -> None:
        """Create history entry for order update"""
        db = await get_database()
        
        # Get changes from event data
        changes = event.data.get("changes", {})
        # Serialize changes to JSON string
        changes_json = json.dumps(changes) if changes else None
        
        await db.orderhistory.create(
            data={
                "orderId": event.data["order_id"],
                "action": "UPDATED",
                "changes": changes_json,
                "performedBy": event.data.get("new_data", {}).get("customerId")
            }
        )
        
        self.logger.info(f"Created history entry for order update {event.data['order_id']}")
    
    async def _handle_order_deleted(self, event: Event) -> None:
        """Create history entry for order deletion"""
        db = await get_database()

        # Get order data from event data
        order_data = event.data.get("order_data", {})

        # Prepare changes data
        changes_data = {
            "deleted_at": "now",  # Có thể thay bằng datetime.now().isoformat() nếu muốn
            "order_info": {
                "id": order_data.get("id"),
                "customerId": order_data.get("customerId"),
                "status": order_data.get("status")
            }
        }

        # Serialize changes to JSON string
        changes_json = json.dumps(changes_data) if changes_data else None

        await db.orderhistory.create(
            data={
                "orderId": event.data["order_id"],
                "action": "DELETED",
                "changes": changes_json,
                "performedBy": event.data.get("order_data", {}).get("customerId")
            }
        )
        
        self.logger.info(f"Created history entry for order deletion {event.data['order_id']}")
