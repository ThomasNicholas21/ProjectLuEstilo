from pydantic import BaseModel, Field, constr
from enum import Enum
from typing import Optional
from pydantic import ConfigDict


class UserRole(str, Enum):
    ADMIN = "admin"
    REGULAR = "regular"  


class UserRegister(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., examples="thomas", description="Nome de usuário único") # type: ignore
    password: constr(min_length=6) = Field(..., examples="secret123", description="Senha com mínimo de 6 caracteres") # type: ignore
    role: UserRole = Field(examples=UserRole.REGULAR, description="Papel do usuário (admin ou regular)")

    model_config = ConfigDict(json_schema_extra={
        "examples": {
            "username": "thomas",
            "password": "secret123",
            "role": "regular"
        }
    })


class UserLogin(BaseModel):
    username: str = Field(..., examples="thomas")
    password: str = Field(..., examples="secret123")


class UserResponse(BaseModel):
<<<<<<< HEAD
    id_user: int = Field(example=1)
    username: str = Field(example="john_doe")
    role: UserRole = Field(example=UserRole.REGULAR)
=======
    id_user: int = Field(examples=1)
    username: str = Field(examples="john_doe")
    role: UserRole = Field(examples=UserRole.REGULAR)
>>>>>>> 5479eb99dcc1635d826877d8031cabe2dc8ff790
    model_config = ConfigDict(from_attributes=True) 


class TokenResponse(BaseModel):
    access_token: str = Field(..., examples="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., examples="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", examples="bearer")


class TokenRefreshRequest(BaseModel):
<<<<<<< HEAD
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
=======
    refresh_token: str = Field(..., examples="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
>>>>>>> 5479eb99dcc1635d826877d8031cabe2dc8ff790
