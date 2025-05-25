from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from pydantic import ConfigDict


class EmptyStrToNoneMixin:
    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, value):
        return None if value == "" else value


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples="Camiseta Básica", description="Nome do produto")
    bar_code: str = Field(..., min_length=1, max_length=50, examples="7891234567890", description="Código de barras único")
    description: Optional[str] = Field(None, examples="Camiseta 100% algodão", description="Descrição detalhada")
    price: float = Field(..., gt=0, examples=49.90, description="Preço de venda (maior que 0)")
    stock: int = Field(..., ge=0, examples=100, description="Quantidade em estoque (não negativo)")
    valid_date: Optional[datetime] = Field(None, examples="2025-12-31T23:59:59", description="Data de validade quando aplicável")
    category: Optional[str] = Field(None, max_length=50, examples="Vestuário", description="Categoria do produto")
    section: Optional[str] = Field(None, max_length=50, examples="Moda", description="Seção do produto")
    images: Optional[str] = Field(None, examples="http://examples.com/image.jpg", description="URLs de imagens separadas por vírgula")

    model_config = ConfigDict(json_schema_extra={
        "examples": {
            "name": "Tênis Esportivo",
            "bar_code": "7896541230365",
            "price": 299.90,
            "stock": 50
        }
    })


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    bar_code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    valid_date: Optional[datetime] = None
    category: Optional[str] = Field(None, max_length=50)
    section: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(json_schema_extra={
        "examples": {
            "price": 259.90,
            "stock": 30
        }
    })


class ProductResponse(ProductBase):
<<<<<<< HEAD
    id_product: int = Field(..., example=1)
=======
    id_product: int = Field(..., examples=1)
>>>>>>> 5479eb99dcc1635d826877d8031cabe2dc8ff790
    model_config = ConfigDict(from_attributes=True)
