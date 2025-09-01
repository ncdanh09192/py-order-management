import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.events.event_bus import EventBus
from app.events.base import Event, EventHandler
import asyncio


class MockEvent(Event):
    """Mock event for testing"""
    def __init__(self, event_id: str = "test_event_123"):
        super().__init__("MockEvent", {"id": event_id})


class MockEventHandler(EventHandler):
    """Mock event handler for testing"""
    def __init__(self, name: str = "MockHandler"):
        self.name = name
        self.handled_events = []
    
    def can_handle(self, event: Event) -> bool:
        return True
    
    async def handle(self, event: Event) -> None:
        self.handled_events.append(event)
        await asyncio.sleep(0.001)  # Simulate async work


class MockAsyncEventHandler(EventHandler):
    """Mock async event handler for testing"""
    def __init__(self, name: str = "AsyncMockHandler", should_fail: bool = False):
        self.name = name
        self.handled_events = []
        self.should_fail = should_fail
    
    def can_handle(self, event: Event) -> bool:
        return True
    
    async def handle(self, event: Event) -> None:
        if self.should_fail:
            raise Exception(f"Handler {self.name} failed intentionally")
        self.handled_events.append(event)
        await asyncio.sleep(0.001)  # Simulate async work


class TestEventBus:
    """Test cases for EventBus"""
    
    @pytest.fixture
    def event_bus(self):
        return EventBus()
    
    @pytest.fixture
    def mock_event(self):
        return MockEvent()
    
    @pytest.fixture
    def mock_handler(self):
        return MockEventHandler()
    
    @pytest.fixture
    def mock_async_handler(self):
        return MockAsyncEventHandler()
    
    @pytest.fixture
    def failing_handler(self):
        return MockAsyncEventHandler("FailingHandler", should_fail=True)
    
    def test_event_bus_initialization(self, event_bus):
        """Test EventBus initialization"""
        assert event_bus.handlers == []
        assert len(event_bus.event_history) == 0
    
    def test_register_handler(self, event_bus, mock_handler):
        """Test registering a single handler"""
        event_bus.register_handler(mock_handler)
        
        assert len(event_bus.handlers) == 1
        assert event_bus.handlers[0] == mock_handler
    
    def test_register_multiple_handlers(self, event_bus, mock_handler, mock_async_handler):
        """Test registering multiple handlers"""
        handlers = [mock_handler, mock_async_handler]
        event_bus.register_handlers(handlers)
        
        assert len(event_bus.handlers) == 2
        assert mock_handler in event_bus.handlers
        assert mock_async_handler in event_bus.handlers
    
    @pytest.mark.asyncio
    async def test_publish_event_no_handlers(self, event_bus, mock_event):
        """Test publishing event when no handlers are registered"""
        await event_bus.publish(mock_event)
        
        # Event should be stored in history
        assert len(event_bus.event_history) == 1
        assert event_bus.event_history[0] == mock_event
    
    @pytest.mark.asyncio
    async def test_publish_event_with_handler(self, event_bus, mock_event, mock_handler):
        """Test publishing event with registered handler"""
        event_bus.register_handler(mock_handler)
        
        await event_bus.publish(mock_event)
        
        # Event should be stored in history
        assert len(event_bus.event_history) == 1
        assert event_bus.event_history[0] == mock_event
        
        # Handler should have processed the event
        assert len(mock_handler.handled_events) == 1
        assert mock_handler.handled_events[0] == mock_event
    
    @pytest.mark.asyncio
    async def test_publish_event_with_multiple_handlers(self, event_bus, mock_event, mock_handler, mock_async_handler):
        """Test publishing event with multiple handlers"""
        event_bus.register_handlers([mock_handler, mock_async_handler])
        
        await event_bus.publish(mock_event)
        
        # Both handlers should have processed the event
        assert len(mock_handler.handled_events) == 1
        assert len(mock_async_handler.handled_events) == 1
        assert mock_handler.handled_events[0] == mock_event
        assert mock_async_handler.handled_events[0] == mock_event
    
    @pytest.mark.asyncio
    async def test_publish_event_with_failing_handler(self, event_bus, mock_event, mock_handler, failing_handler):
        """Test publishing event with one failing handler"""
        event_bus.register_handlers([mock_handler, failing_handler])
        
        # Should not raise exception, but log the error
        await event_bus.publish(mock_event)
        
        # Successful handler should still process the event
        assert len(mock_handler.handled_events) == 1
        assert mock_handler.handled_events[0] == mock_event
        
        # Failing handler should not have processed the event
        assert len(failing_handler.handled_events) == 0
    
    def test_get_event_history_all(self, event_bus, mock_event):
        """Test getting all event history"""
        event_bus.event_history = [mock_event]
        
        history = event_bus.get_event_history()
        assert len(history) == 1
        assert history[0] == mock_event
    
    def test_get_event_history_by_type(self, event_bus):
        """Test getting event history filtered by type"""
        # Create a fresh event bus for this test to avoid interference
        fresh_event_bus = EventBus()
        
        event1 = MockEvent("event1")
        event2 = MockEvent("event2")
        fresh_event_bus.event_history = [event1, event2]
        
        # Debug: print what we have
        print(f"Event history length: {len(fresh_event_bus.event_history)}")
        print(f"Event types: {[event.event_type for event in fresh_event_bus.event_history]}")
        
        history = fresh_event_bus.get_event_history("MockEvent")
        print(f"Filtered history length: {len(history)}")
        print(f"Filtered event types: {[event.event_type for event in history]}")
        
        assert len(history) == 2
        assert all(event.event_type == "MockEvent" for event in history)
    
    def test_get_event_history_empty(self, event_bus):
        """Test getting event history when empty"""
        history = event_bus.get_event_history()
        assert len(history) == 0
    
    @pytest.mark.asyncio
    async def test_handler_execution_timing(self, event_bus, mock_event, mock_async_handler):
        """Test that handler execution timing is logged"""
        event_bus.register_handler(mock_async_handler)
        
        # Mock the instance logger, not the module logger
        with patch.object(event_bus, 'logger') as mock_logger:
            await event_bus.publish(mock_event)
            
            # Verify that timing info was logged
            mock_logger.info.assert_called()
            
            # Check if any of the info calls contain timing information
            info_calls = [str(call) for call in mock_logger.info.call_args_list]
            timing_found = any("completed in" in call for call in info_calls)
            assert timing_found, "Timing information should be logged"
    
    @pytest.mark.asyncio
    async def test_concurrent_handler_execution(self, event_bus, mock_event):
        """Test that handlers execute concurrently"""
        import time
        
        class SlowHandler(EventHandler):
            def __init__(self, name: str, delay: float):
                self.name = name
                self.delay = delay
                self.start_time = None
                self.end_time = None
            
            def can_handle(self, event: Event) -> bool:
                return True
            
            async def handle(self, event: Event) -> None:
                self.start_time = time.time()
                await asyncio.sleep(self.delay)
                self.end_time = time.time()
        
        # Create two handlers with different delays
        slow_handler = SlowHandler("SlowHandler", 0.1)
        fast_handler = SlowHandler("FastHandler", 0.05)
        
        event_bus.register_handlers([slow_handler, fast_handler])
        
        start_time = time.time()
        await event_bus.publish(mock_event)
        end_time = time.time()
        
        # Total execution time should be close to the slowest handler (0.1s)
        # not the sum of both (0.15s)
        execution_time = end_time - start_time
        assert execution_time < 0.15  # Should be concurrent
        assert execution_time > 0.09   # But not faster than slowest handler
