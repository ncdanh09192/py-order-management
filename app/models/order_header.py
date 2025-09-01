from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

class OrderHeader:
    """Order Header model"""
    def __init__(
        self,
        id: int,
        customer_id: int,
        order_date: datetime,
        status: OrderStatus,
        total_amount: Decimal,
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = id
        self.customer_id = customer_id
        self.order_date = order_date
        self.status = status
        self.total_amount = total_amount
        self.created_at = created_at
        self.updated_at = updated_at
