from pydantic import BaseModel, Field, ConfigDict


class OrderItemBase(BaseModel):
    id_product: int = Field(..., examples=1, description="ID do produto")
    amount: int = Field(..., examples=2, ge=1, description="Quantidade do produto")


class OrderItemCreate(OrderItemBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": {"id_product": 1, "amount": 3}
        }
    )


class OrderItemUpdate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id_orderitem: int = Field(..., examples=1)
    unit_price: float = Field(..., examples=99.90)
    model_config = ConfigDict(from_attributes=True)
