from typing import List
from app.events.base import Event, EventHandler
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class EventBus:
    """Central event bus for publishing and handling events"""
    
    def __init__(self):
        self.handlers: List[EventHandler] = []
        self.logger = logging.getLogger(__name__)
        self.event_history: List[Event] = []
    
    def register_handler(self, handler: EventHandler) -> None:
        """Register an event handler"""
        self.handlers.append(handler)
        self.logger.info(f"Registered handler: {handler.__class__.__name__}")
    
    def register_handlers(self, handlers: List[EventHandler]) -> None:
        """Register multiple handlers at once"""
        for handler in handlers:
            self.register_handler(handler)
    
    async def publish(self, event: Event) -> None:
        """Publish an event to all registered handlers"""
        self.logger.info(f"Publishing event: {event.event_type} (ID: {event.event_id})")
        
        # Store event in history (for debugging)
        self.event_history.append(event)
        
        # Find handlers that can handle this event
        relevant_handlers = [
            handler for handler in self.handlers 
            if handler.can_handle(event)
        ]
        
        if not relevant_handlers:
            self.logger.warning(f"No handlers found for event: {event.event_type}")
            return
        
        # Execute handlers concurrently
        tasks = []
        for handler in relevant_handlers:
            task = self._execute_handler(handler, event)
            tasks.append(task)
        
        # Wait for all handlers to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Handler {relevant_handlers[i].__class__.__name__} failed: {str(result)}")
            else:
                self.logger.info(f"Handler {relevant_handlers[i].__class__.__name__} completed successfully")
    
    async def _execute_handler(self, handler: EventHandler, event: Event) -> None:
        """Execute a single handler with error handling"""
        try:
            start_time = datetime.utcnow()
            await handler.handle(event)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info(f"Handler {handler.__class__.__name__} completed in {duration:.3f}s")
            
        except Exception as e:
            self.logger.error(f"Error in handler {handler.__class__.__name__}: {str(e)}")
            raise
    
    def get_event_history(self, event_type: str = None) -> List[Event]:
        """Get event history for debugging/monitoring"""
        if event_type:
            return [event for event in self.event_history if event.event_type == event_type]
        return self.event_history
