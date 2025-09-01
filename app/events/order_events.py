from app.events.base import Event
from typing import Dict, Any

class OrderCreatedEvent(Event):
    """Event fired when a new order is created"""
    
    def __init__(self, order_data: Dict[str, Any]):
        super().__init__("OrderCreated", order_data)
        
        # Validate required fields
        required_fields = ["id", "customerId", "orderDate", "status"]
        for field in required_fields:
            if field not in order_data:
                raise ValueError(f"Missing required field: {field}")

class OrderUpdatedEvent(Event):
    """Event fired when an order is updated"""
    
    def __init__(self, order_id: int, old_data: Dict[str, Any], new_data: Dict[str, Any]):
        super().__init__("OrderUpdated", {
            "order_id": order_id,
            "old_data": old_data,
            "new_data": new_data,
            "changes": self._calculate_changes(old_data, new_data)
        })
    
    def _calculate_changes(self, old_data: Dict, new_data: Dict) -> Dict[str, Any]:
        """Calculate what fields changed"""
        changes = {}
        for key in new_data:
            if key in old_data and old_data[key] != new_data[key]:
                changes[key] = {
                    "from": old_data[key],
                    "to": new_data[key]
                }
        return changes

class OrderDeletedEvent(Event):
    """Event fired when an order is deleted"""
    
    def __init__(self, order_id: int, order_data: Dict[str, Any]):
        super().__init__("OrderDeleted", {
            "order_id": order_id,
            "order_data": order_data
        })
