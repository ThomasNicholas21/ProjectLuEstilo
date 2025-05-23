from pydantic import BaseModel, EmailStr, field_validator
from .utils.cpf_validator import cpf_validador


class CPFValidatorMixin:
    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        value = value.strip()
        if cpf_validador(value):
            raise ValueError("CPF inválido.")
        return value


class ClientBase(BaseModel, CPFValidatorMixin):
    name: str
    cpf: str
    email: EmailStr
    phone: str


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel, CPFValidatorMixin):
    name: str | None = None
    cpf: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class ClientResponse(ClientBase):
    id_client: int

    class Config:
        orm_mode = True
