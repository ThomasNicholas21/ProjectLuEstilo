from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum
from .orderitem import OrderItemCreate, OrderItemResponse, OrderItemUpdate


class OrderStatusEnum(str, Enum):
    pendente = "pendente"
    pago = "pago"
    cancelado = "cancelado"
    em_andamento = "em_andamento"
    finalizado = "finalizado"


class OrderBase(BaseModel):
    id_client: int
    status: OrderStatusEnum


class OrderCreate(OrderBase):
    products: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    id_client: Optional[int] = None
    status: Optional[OrderStatusEnum] = None
    products: Optional[List[OrderItemUpdate]] = None


class OrderResponse(BaseModel):
    id_order: int
    id_client: int
    total_amount: int
    total_price: float
    status: OrderStatusEnum
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True