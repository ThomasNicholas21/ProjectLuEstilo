from pydantic import BaseModel, Field, constr
from enum import Enum
from typing import Optional
from pydantic import ConfigDict


class UserRole(str, Enum):
    ADMIN = "admin"
    REGULAR = "regular"  


class UserRegister(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., example="thomas", description="Nome de usuário único") # type: ignore
    password: constr(min_length=6) = Field(..., example="secret123", description="Senha com mínimo de 6 caracteres") # type: ignore
    role: UserRole = Field(example=UserRole.REGULAR, description="Papel do usuário (admin ou regular)")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "username": "thomas",
            "password": "secret123",
            "role": "regular"
        }
    })


class UserLogin(BaseModel):
    username: str = Field(..., example="thomas")
    password: str = Field(..., example="secret123")


class UserResponse(BaseModel):
    id_user: int = Field(example=1)
    username: str = Field(example="john_doe")
    role: UserRole = Field(example=UserRole.REGULAR)

    class Config:
        from_attributes=True


class TokenResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", example="bearer")


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")