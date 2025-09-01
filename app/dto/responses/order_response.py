from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal
from datetime import date, datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

class OrderLineResponse(BaseModel):
    """Response DTO for order line"""
    id: int
    product_id: int = Field(..., alias="productId")
    quantity: int
    unit_price: Decimal = Field(..., alias="unitPrice")
    created_at: datetime = Field(..., alias="createdAt")
    
    class Config:
        allow_population_by_field_name = True

class OrderResponse(BaseModel):
    """Response DTO for order"""
    id: int
    customer_id: int = Field(..., alias="customerId")
    order_date: datetime = Field(..., alias="orderDate")
    status: OrderStatus
    total_amount: Decimal = Field(..., alias="totalAmount")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    lines: List[OrderLineResponse]
    
    class Config:
        allow_population_by_field_name = True

class OrderListResponse(BaseModel):
    """Response DTO for order list"""
    orders: List[OrderResponse]
    total: int
    page: int
    size: int
    has_next: bool = Field(..., alias="hasNext")
    has_prev: bool = Field(..., alias="hasPrev")
    
    class Config:
        allow_population_by_field_name = True
