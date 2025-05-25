from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from enum import Enum
from .orderitem import OrderItemCreate, OrderItemResponse, OrderItemUpdate


class OrderStatusEnum(str, Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADO = "finalizado"


class OrderBase(BaseModel):
    id_client: int = Field(..., example=1, description="ID do cliente associado")
    status: OrderStatusEnum = Field(..., example=OrderStatusEnum.PENDENTE)


class OrderCreate(OrderBase):
    products: List[OrderItemCreate] = Field(..., min_items=1)
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "id_client": 1,
                "status": "pendente",
                "products": [{"id_product": 1, "amount": 2}]
            }
        }
    )


class OrderUpdate(BaseModel):
    id_client: Optional[int] = Field(None, example=1)
    status: Optional[OrderStatusEnum] = Field(None, example=OrderStatusEnum.PAGO)
    products: Optional[List[OrderItemUpdate]] = Field(None, min_items=1)


class OrderResponse(OrderBase):
    id_order: int = Field(..., example=1)
    total_amount: int = Field(..., example=5)
    total_price: float = Field(..., example=499.50)
    created_at: datetime = Field(..., example="2024-01-01T12:00:00Z")
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True
