from pydantic import BaseModel, Field, ConfigDict


class OrderItemBase(BaseModel):
    id_product: int = Field(..., example=1, description="ID do produto")
    amount: int = Field(..., example=2, ge=1, description="Quantidade do produto")


class OrderItemCreate(OrderItemBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id_product": 1, "amount": 3}
        }
    )


class OrderItemUpdate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id_orderitem: int = Field(..., example=1)
    unit_price: float = Field(..., example=99.90)
    model_config = ConfigDict(from_attributes=True)
