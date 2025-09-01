from pydantic import BaseModel, validator, Field
from typing import List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

class CreateOrderLineRequest(BaseModel):
    """Request DTO for creating order line"""
    product_id: int = Field(..., gt=0, description="Product ID must be positive")
    quantity: int = Field(..., gt=0, le=1000, description="Quantity between 1-1000")
    unit_price: Decimal = Field(..., ge=Decimal('0'), le=Decimal('999999.99'), description="Unit price between 0-999999.99")
    
    @validator('unit_price')
    def validate_unit_price(cls, v):
        if v > Decimal('999999.99'):
            raise ValueError('Unit price too high')
        return v

class CreateOrderRequest(BaseModel):
    """Request DTO for creating order"""
    customer_id: int = Field(..., gt=0, description="Customer ID must be positive")
    order_date: datetime = Field(..., description="Order date")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    lines: List[CreateOrderLineRequest] = Field(..., min_items=1, max_items=50, description="Order lines")
    
    @validator('lines')
    def validate_lines(cls, v):
        if not v:
            raise ValueError('Order must have at least one line')
        return v
    
    @validator('order_date')
    def validate_order_date(cls, v):
        if v > datetime.now():
            raise ValueError('Order date cannot be in the future')
        return v

class UpdateOrderRequest(BaseModel):
    """Request DTO for updating order"""
    status: OrderStatus = Field(..., description="New order status")
    
    @validator('status')
    def validate_status(cls, v):
        if v == OrderStatus.CANCELLED:
            # Add additional validation for cancellation if needed
            pass
        return v
