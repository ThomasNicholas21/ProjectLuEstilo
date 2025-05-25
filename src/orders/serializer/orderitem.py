from pydantic import BaseModel


class OrderItemBase(BaseModel):
    id_product: int
    amount: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    id_product: int
    amount: int


class OrderItemResponse(OrderItemBase):
    id_orderitem: int
    unit_price: float


    class Config:
        from_attributes = True
