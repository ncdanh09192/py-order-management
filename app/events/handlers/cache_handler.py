from app.events.base import EventHandler, Event
from app.cache.redis_client import redis_client
import json
import logging

logger = logging.getLogger(__name__)

class CacheHandler(EventHandler):
    """Handles caching operations for order events"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def can_handle(self, event: Event) -> bool:
        """Check if this handler can handle the event"""
        return event.event_type in ["OrderCreated", "OrderUpdated", "OrderDeleted"]
    
    async def handle(self, event: Event) -> None:
        """Handle the event"""
        self.logger.info(f"CacheHandler processing {event.event_type}")
        
        if event.event_type == "OrderCreated":
            await self._handle_order_created(event)
        elif event.event_type == "OrderUpdated":
            await self._handle_order_updated(event)
        elif event.event_type == "OrderDeleted":
            await self._handle_order_deleted(event)
    
    async def _handle_order_created(self, event: Event) -> None:
        """Handle order creation - cache the order"""
        order_data = event.data
        cache_key = f"order:{order_data['id']}"
        
        try:
            # Cache order data with 1 hour expiration
            await redis_client.set(cache_key, json.dumps(order_data), expire=3600)
            self.logger.info(f"Cached order {order_data['id']} successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to cache order {order_data['id']}: {str(e)}")
    
    async def _handle_order_updated(self, event: Event) -> None:
        """Handle order update - update cache"""
        order_id = event.data["order_id"]
        new_data = event.data["new_data"]
        cache_key = f"order:{order_id}"
        
        try:
            # Update cache with new data
            await redis_client.set(cache_key, json.dumps(new_data), expire=3600)
            self.logger.info(f"Updated cache for order {order_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to update cache for order {order_id}: {str(e)}")
    
    async def _handle_order_deleted(self, event: Event) -> None:
        """Handle order deletion - remove from cache"""
        order_id = event.data["order_id"]
        cache_key = f"order:{order_id}"
        
        try:
            # Remove from cache
            await redis_client.delete(cache_key)
            self.logger.info(f"Removed order {order_id} from cache")
            
        except Exception as e:
            self.logger.error(f"Failed to remove order {order_id} from cache: {str(e)}")
