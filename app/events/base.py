from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime
import json
import uuid

class Event(ABC):
    """Base class for all events"""
    
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_id = str(uuid.uuid4())
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.utcnow()
        self.correlation_id = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict(), default=str)

class EventHandler(ABC):
    """Base class for event handlers"""
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle the event"""
        pass
    
    @abstractmethod
    def can_handle(self, event: Event) -> bool:
        """Check if this handler can handle the event"""
        pass
