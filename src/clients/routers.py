from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List
from src.common.database import get_db
from .models import Client
from .schemas import ClientCreate, ClientUpdate, ClientResponse
from src.auth.security.token import get_current_user 


client_router = APIRouter(
    prefix="/clients",
    tags=["Clientes"],
    responses={
        403: {"description": "Acesso negado"},
        401: {"description": "Credenciais inválidas"}
    }
)


def check_admin_permission(current_user: dict):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )


@client_router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo cliente",
    responses={
        201: {"description": "Cliente criado com sucesso"},
        400: {"description": "CPF ou email já cadastrado"}
    }
)
async def post_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) 
):
    check_admin_permission(current_user)
    
    try:
        db_client = Client(**client.model_dump())
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF ou email já cadastrado"
        )


@client_router.get("/", response_model=List[ClientResponse])
async def get_client(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0), 
    limit: int = Query(default=10, ge=1), 
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Client)

        if name:
            query = query.filter(Client.name.ilike(f"%{name}%"))

        if email:
            query = query.filter(Client.email.ilike(f"%{email}%"))

        clients = query.offset(skip).limit(limit).all()

        return clients

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar clientes: {e}")


@client_router.get("/{id_client}", response_model=ClientResponse)
async def get_detail_client(id_client: str , db: Session = Depends(get_db)):
    try:
        client = db.query(Client).get(id_client)

        if not client: 
                raise HTTPException(status_code=404, detail="Cliente não encontrado")

        return client
    
    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {e}")
    

@client_router.put("/{id_client}", response_model=ClientResponse)
async def put_detail_client(id_client: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    try:
        client = db.query(Client).get(id_client)

        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

        update_data = client_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(client, key, value)

        db.commit()
        db.refresh(client)
        return client

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cliente: {str(e)}")


@client_router.delete("/{id_client}", response_model=ClientResponse)
async def delete_detail_client(id_client: int, db: Session = Depends(get_db)):
    try:
        client = db.query(Client).get(id_client)

        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        db.delete(client)
        db.commit()

        return client

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar cliente: {str(e)}")
    