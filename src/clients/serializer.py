from pydantic import BaseModel, EmailStr, field_validator
from .utils.cpf_validator import cpf_validador


class ClientBase(BaseModel):
    name: str
    cpf: str
    email: EmailStr
    phone: str

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        # remove espaços, se quiser
        value = value.strip()
        if not cpf_validador(value):
            raise ValueError("CPF inválido.")
        return value

class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id_client: int

    class Config:
        orm_mode = True
