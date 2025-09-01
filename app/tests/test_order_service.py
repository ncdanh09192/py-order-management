import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime
from app.services.order_service import OrderService
from app.events.event_bus import EventBus
from app.dto.requests.order_request import CreateOrderRequest, UpdateOrderRequest, CreateOrderLineRequest
from app.dto.responses.order_response import OrderListResponse
from app.events.order_events import OrderCreatedEvent, OrderUpdatedEvent, OrderDeletedEvent


class TestOrderService:
    """Test cases for OrderService"""
    
    @pytest.fixture
    def mock_event_bus(self):
        return Mock(spec=EventBus)
    
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        
        # Mock order header with proper datetime objects
        mock_header = Mock()
        mock_header.id = 1
        mock_header.customerId = 123
        mock_header.orderDate = datetime(2025, 1, 20)
        mock_header.status = "PENDING"
        mock_header.totalAmount = Decimal("50.00")
        mock_header.createdAt = datetime(2025, 1, 20, 10, 0, 0)
        mock_header.updatedAt = datetime(2025, 1, 20, 10, 0, 0)
        
        # Mock order lines with proper datetime objects
        mock_line1 = Mock()
        mock_line1.id = 1
        mock_line1.productId = 1001
        mock_line1.quantity = 2
        mock_line1.unitPrice = Decimal("25.00")
        mock_line1.createdAt = datetime(2025, 1, 20, 10, 0, 0)
        
        mock_line2 = Mock()
        mock_line2.id = 2
        mock_line2.productId = 1002
        mock_line2.quantity = 1
        mock_line2.unitPrice = Decimal("15.00")
        mock_line2.createdAt = datetime(2025, 1, 20, 10, 0, 0)
        
        mock_header.lines = [mock_line1, mock_line2]
        
        # Mock database operations
        db.orderheader.create = AsyncMock(return_value=mock_header)
        db.orderline.create = AsyncMock(side_effect=[mock_line1, mock_line2])
        db.orderheader.find_first = AsyncMock(return_value=mock_header)
        db.orderheader.update = AsyncMock(return_value=mock_header)
        db.orderheader.delete = AsyncMock(return_value=mock_header)
        db.orderheader.count = AsyncMock(return_value=1)
        db.orderheader.find_many = AsyncMock(return_value=[mock_header])
        
        return db
    
    @pytest.fixture
    def mock_redis(self):
        redis = Mock()
        redis.get = AsyncMock(return_value=None)
        redis.set = AsyncMock()
        return redis
    
    @pytest.fixture
    def create_order_request(self):
        return CreateOrderRequest(
            customer_id=123,
            order_date=datetime(2025, 1, 20),
            status="PENDING",
            lines=[
                CreateOrderLineRequest(product_id=1001, quantity=2, unit_price=Decimal("25.00")),
                CreateOrderLineRequest(product_id=1002, quantity=1, unit_price=Decimal("15.00"))
            ]
        )
    
    @pytest.fixture
    def update_order_request(self):
        return UpdateOrderRequest(status="SHIPPED")
    
    @pytest.fixture
    def order_service(self, mock_event_bus):
        return OrderService(mock_event_bus)
    
    def test_calculate_total_amount(self, order_service):
        """Test total amount calculation"""
        lines = [
            Mock(unit_price=Decimal("25.00"), quantity=2),
            Mock(unit_price=Decimal("15.00"), quantity=1)
        ]
        
        total = order_service._calculate_total_amount(lines)
        expected = Decimal("25.00") * 2 + Decimal("15.00") * 1
        assert total == expected
    
    def test_calculate_total_amount_empty_lines(self, order_service):
        """Test total amount calculation with empty lines"""
        lines = []
        total = order_service._calculate_total_amount(lines)
        assert total == Decimal("0")
    
    def test_calculate_total_amount_zero_prices(self, order_service):
        """Test total amount calculation with zero prices"""
        lines = [
            Mock(unit_price=Decimal("0"), quantity=5),
            Mock(unit_price=Decimal("10.00"), quantity=0)
        ]
        
        total = order_service._calculate_total_amount(lines)
        assert total == Decimal("0")
    
    @pytest.mark.asyncio
    async def test_create_order_success(self, order_service, mock_event_bus, create_order_request, mock_db):
        """Test successful order creation"""
        with patch('app.services.order_service.get_database', return_value=mock_db):
            result = await order_service.create_order(create_order_request, 123)
            
            # Verify result structure
            assert result["id"] == 1
            assert result["customerId"] == 123
            assert result["status"] == "PENDING"
            assert result["totalAmount"] == Decimal("50.00")
            assert len(result["lines"]) == 2
            
            # Verify database calls
            mock_db.orderheader.create.assert_called_once()
            assert mock_db.orderline.create.call_count == 2
            
            # Verify event publishing
            mock_event_bus.publish.assert_called_once()
            published_event = mock_event_bus.publish.call_args[0][0]
            assert isinstance(published_event, OrderCreatedEvent)
    
    @pytest.mark.asyncio
    async def test_create_order_database_error(self, order_service, mock_event_bus, create_order_request):
        """Test order creation with database error"""
        mock_db = Mock()
        mock_db.orderheader.create = AsyncMock(side_effect=Exception("Database error"))
        
        with patch('app.services.order_service.get_database', return_value=mock_db):
            with pytest.raises(Exception, match="Database error"):
                await order_service.create_order(create_order_request, 123)
    
    @pytest.mark.asyncio
    async def test_get_order_by_id_from_cache(self, order_service, mock_event_bus, mock_redis):
        """Test getting order from cache"""
        with patch('app.services.order_service.redis_client', mock_redis):
            mock_redis.get.return_value = '{"id": 1, "customerId": 123, "status": "PENDING", "totalAmount": 50.00}'
            
            result = await order_service.get_order_by_id(1, 123)
            
            assert result["id"] == 1
            assert result["customerId"] == 123
            mock_redis.get.assert_called_once_with("order:1")
    
    @pytest.mark.asyncio
    async def test_get_order_by_id_from_database(self, order_service, mock_event_bus, mock_db, mock_redis):
        """Test getting order from database when not in cache"""
        with patch('app.services.order_service.get_database', return_value=mock_db), \
             patch('app.services.order_service.redis_client', mock_redis):
            
            result = await order_service.get_order_by_id(1, 123)
            
            assert result["id"] == 1
            assert result["customerId"] == 123
            mock_db.orderheader.find_first.assert_called_once()
            mock_redis.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_order_by_id_not_found(self, order_service, mock_event_bus, mock_db, mock_redis):
        """Test getting non-existent order"""
        mock_db.orderheader.find_first = AsyncMock(return_value=None)
        
        with patch('app.services.order_service.get_database', return_value=mock_db), \
             patch('app.services.order_service.redis_client', mock_redis):
            
            result = await order_service.get_order_by_id(999, 123)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_order_by_id_wrong_owner(self, order_service, mock_event_bus, mock_db, mock_redis):
        """Test getting order with wrong customer ID"""
        with patch('app.services.order_service.redis_client', mock_redis):
            mock_redis.get.return_value = '{"id": 1, "customerId": 456, "status": "PENDING"}'
            
            # Should fall back to database
            with patch('app.services.order_service.get_database', return_value=mock_db):
                result = await order_service.get_order_by_id(1, 123)
                
                # Service doesn't check ownership, so it should return the order
                # Ownership check is done at API level
                assert result is not None
                assert result["id"] == 1
    
    @pytest.mark.asyncio
    async def test_update_order_success(self, order_service, mock_event_bus, update_order_request, mock_db):
        """Test successful order update"""
        # Mock the update to return updated status
        updated_header = Mock()
        updated_header.id = 1
        updated_header.customerId = 123
        updated_header.orderDate = datetime(2025, 1, 20)
        updated_header.status = "SHIPPED"  # Updated status
        updated_header.totalAmount = Decimal("50.00")
        updated_header.createdAt = datetime(2025, 1, 20, 10, 0, 0)
        updated_header.updatedAt = datetime(2025, 1, 20, 10, 0, 0)
        updated_header.lines = []
        
        mock_db.orderheader.update = AsyncMock(return_value=updated_header)
        mock_db.orderheader.find_first = AsyncMock(return_value=updated_header)
        
        with patch('app.services.order_service.get_database', return_value=mock_db):
            result = await order_service.update_order(1, update_order_request, 123)
            
            assert result["id"] == 1
            assert result["status"] == "SHIPPED"
            
            # Verify database update
            mock_db.orderheader.update.assert_called_once_with(
                where={"id": 1},
                data={"status": "SHIPPED"}
            )
            
            # Verify event publishing
            mock_event_bus.publish.assert_called_once()
            published_event = mock_event_bus.publish.call_args[0][0]
            assert isinstance(published_event, OrderUpdatedEvent)
    
    @pytest.mark.asyncio
    async def test_update_order_not_found(self, order_service, mock_event_bus, update_order_request):
        """Test updating non-existent order"""
        mock_db = Mock()
        mock_db.orderheader.find_first = AsyncMock(return_value=None)
        
        with patch('app.services.order_service.get_database', return_value=mock_db):
            result = await order_service.update_order(999, update_order_request, 123)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_order_success(self, order_service, mock_event_bus, mock_db):
        """Test successful order deletion"""
        with patch('app.services.order_service.get_database', return_value=mock_db):
            result = await order_service.delete_order(1, 123)
            
            assert result is True
            
            # Verify event publishing (should happen before deletion)
            mock_event_bus.publish.assert_called_once()
            published_event = mock_event_bus.publish.call_args[0][0]
            assert isinstance(published_event, OrderDeletedEvent)
            
            # Verify database deletion
            mock_db.orderheader.delete.assert_called_once_with(where={"id": 1})
    
    @pytest.mark.asyncio
    async def test_delete_order_not_found(self, order_service, mock_event_bus):
        """Test deleting non-existent order"""
        mock_db = Mock()
        mock_db.orderheader.find_first = AsyncMock(return_value=None)
        
        with patch('app.services.order_service.get_database', return_value=mock_db):
            with pytest.raises(ValueError, match="Order 999 not found"):
                await order_service.delete_order(999, 123)
    
    @pytest.mark.asyncio
    async def test_list_orders_success(self, order_service, mock_event_bus, mock_db):
        """Test successful order listing"""
        with patch('app.services.order_service.get_database', return_value=mock_db):
            result = await order_service.list_orders(123, page=1, size=10)
            
            assert isinstance(result, OrderListResponse)
            assert result.total == 1
            assert result.page == 1
            assert result.size == 10
            assert result.has_next is False
            assert result.has_prev is False
            assert len(result.orders) == 1
            
            # Verify database calls
            mock_db.orderheader.count.assert_called_once()
            mock_db.orderheader.find_many.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_orders_pagination(self, order_service, mock_event_bus):
        """Test order listing with pagination"""
        mock_db = Mock()
        mock_db.orderheader.count = AsyncMock(return_value=25)
        
        mock_order = Mock()
        mock_order.id = 1
        mock_order.customerId = 123
        mock_order.status = "PENDING"
        mock_order.totalAmount = Decimal("50.00")
        mock_order.orderDate = datetime(2025, 1, 20, 10, 0, 0)
        mock_order.createdAt = datetime(2025, 1, 20, 10, 0, 0)
        mock_order.updatedAt = datetime(2025, 1, 20, 10, 0, 0)
        mock_order.lines = []
        
        mock_db.orderheader.find_many = AsyncMock(return_value=[mock_order])
        
        with patch('app.services.order_service.get_database', return_value=mock_db):
            result = await order_service.list_orders(123, page=2, size=10)
            
            assert result.total == 25
            assert result.page == 2
            assert result.size == 10
            assert result.has_next is True
            assert result.has_prev is True
            
            # Verify skip calculation
            mock_db.orderheader.find_many.assert_called_once()
            call_args = mock_db.orderheader.find_many.call_args
            assert call_args[1]["skip"] == 10  # (2-1) * 10
