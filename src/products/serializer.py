from pydantic import BaseModel, constr, field_validator
from typing import Optional
from datetime import datetime


class EmptyStrToNoneMixin:
    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, value):
        if value == "":
            return None
        return value


class ProductBase(BaseModel, EmptyStrToNoneMixin):
    name: constr(min_length=1, max_length=100) # type: ignore
    bar_code: str
    description: Optional[str] = None
    price: float
    stock: int
    valid_date: Optional[datetime] = None
    category: Optional[str] = None
    section: Optional[str] = None


class ProductUpdate(BaseModel, EmptyStrToNoneMixin):
    name: Optional[constr(min_length=1, max_length=100)] = None # type: ignore
    bar_code: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    valid_date: Optional[datetime] = None
    category: Optional[str] = None
    section: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id_product: int
    images: Optional[str] = None

    class Config:
        from_attributes = True
