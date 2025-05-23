# src/schemas/client.py
from pydantic import BaseModel


class ClientBase(BaseModel):
    name: str
    cpf: str
    email: str
    phone: str


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id_client: int

    class Config:
        orm_mode = True
