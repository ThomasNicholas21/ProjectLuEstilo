from pydantic import BaseModel, constr
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "regular"


class UserRegister(BaseModel):
    username: constr(min_length=3, max_length=50) # type: ignore
    password: constr(min_length=6) # type: ignore
    role: UserRole


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id_user: int
    username: str
    role: UserRole

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
