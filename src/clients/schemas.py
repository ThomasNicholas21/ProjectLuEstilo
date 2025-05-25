from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from src.utils.cpf_validator import cpf_validator

class CPFValidatorMixin:
    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        value = value.strip()
        if not cpf_validator(value):
            raise ValueError("CPF inválido")
        return value


class ClientBase(BaseModel, CPFValidatorMixin):
    name: str = Field(..., examples="João Silva", min_length=3, max_length=100)
    cpf: str = Field(..., examples="123.456.789-09", description="CPF válido (com ou sem formatação)")
    email: EmailStr = Field(..., examples="joao@email.com")
    phone: str | None = Field(None, examples="(11) 99999-9999")


class ClientCreate(ClientBase):
    model_config = ConfigDict(json_schema_extra={
            "examples": {
                "name": "Maria Souza",
                "cpf": "987.654.321-00",
                "email": "maria@email.com",
                "phone": "(21) 98888-7777"
            }
        }
    )


class ClientUpdate(BaseModel, CPFValidatorMixin):
    name: str | None = Field(None, examples="João Silva Updated")
    cpf: str | None = Field(None, examples="111.222.333-44")
    email: EmailStr | None = Field(None, examples="novo_email@email.com")
    phone: str | None = Field(None, examples="(31) 97777-6666")


class ClientResponse(ClientBase):
    id_client: int = Field(..., examples=1)
    model_config = ConfigDict(from_attributes=True)
