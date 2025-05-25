from pydantic import BaseModel, constr, field_validator
from typing import Optional
from datetime import datetime


class EmptyStrToNoneMixin:
    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, value):
        return None if value == "" else value


class ProductBase(BaseModel, EmptyStrToNoneMixin):
    name: constr(min_length=1, max_length=100)  # type: ignore
    bar_code: constr(min_length=1, max_length=50)  # type: ignore
    description: Optional[str] = None
    price: float
    stock: int
    valid_date: Optional[datetime] = None
    images: Optional[str] = None
    category: Optional[constr(max_length=50)] = None # type: ignore
    section: Optional[constr(max_length=50)] = None # type: ignore


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel, EmptyStrToNoneMixin):
    name: Optional[constr(min_length=1, max_length=100)] = None  # type: ignore
    bar_code: Optional[constr(min_length=1, max_length=50)] = None  # type: ignore
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    valid_date: Optional[datetime] = None
    category: Optional[constr(max_length=50)] = None # type: ignore
    section: Optional[constr(max_length=50)] = None # type: ignore


class ProductResponse(ProductBase):
    id_product: int

    class Config:
        from_attributes = True
