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
                "changes": None,
                "performedBy": event.data["customerId"]
            }
        )
        
        self.logger.info(f"Created history entry for order {event.data['id']}")
    
    async def _handle_order_updated(self, event: Event) -> None:
        """Create history entry for order update"""
        db = await get_database()
        
        changes = event.data.get("changes", {})
        await db.orderhistory.create(
            data={
                "orderId": event.data["order_id"],
                "action": "UPDATED",
                "changes": changes,
                "performedBy": event.data["new_data"]["customerId"]
            }
        )
        
        self.logger.info(f"Created history entry for order update {event.data['order_id']}")
    
    async def _handle_order_deleted(self, event: Event) -> None:
        """Create history entry for order deletion"""
        db = await get_database()
        
        await db.orderhistory.create(
            data={
                "orderId": event.data["order_id"],
                "action": "DELETED",
                "changes": {"deleted_data": event.data["order_data"]},
                "performedBy": event.data["order_data"]["customerId"]
            }
        )
        
        self.logger.info(f"Created history entry for order deletion {event.data['order_id']}")
