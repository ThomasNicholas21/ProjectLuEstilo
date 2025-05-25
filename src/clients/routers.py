from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List
from src.common.database import get_db
from .models import Client
from .schemas import ClientCreate, ClientUpdate, ClientResponse
from src.auth.security.token import get_current_user 
from src.utils.role_validator import check_admin_permission


client_router = APIRouter(
    prefix="/clients",
    tags=["Clientes"],
    responses={
        403: {"description": "Acesso negado"},
        401: {"description": "Credenciais inválidas"}
    }
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
    
    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar clientes"
        )
    
    except Exception as e:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )


@client_router.get(
    "/",
    response_model=List[ClientResponse],
    summary="Listar clientes",
    responses={200: {"description": "Lista de clientes paginada"}}
)
async def get_client(
    name: str | None = Query(None, examples="João"),
    email: str | None = Query(None, examples="joao@email.com"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) 
):
    try:
        query = db.query(Client)
        if name: query = query.filter(Client.name.ilike(f"%{name}%"))
        if email: query = query.filter(Client.email.ilike(f"%{email}%"))

        return query.offset(skip).limit(limit).all()
    
    except HTTPException as e:
        raise 
    
    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar clientes"
        )
    
    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )
    

@client_router.get(
    "/{id_client}",
    response_model=ClientResponse,
    summary="Detalhes de um cliente",
    responses={
        200: {"description": "Cliente encontrado com sucesso"},
        404: {"description": "Cliente não encontrado"}
    }
)
async def get_detail_client(
    id_client: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        client = db.get(Client, id_client)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        return client
    
    except HTTPException as e:
        raise 

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar cliente"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )


@client_router.put(
    "/{id_client}",
    response_model=ClientResponse,
    summary="Atualizar cliente",
    responses={404: {"description": "Cliente não encontrado"}}
)
async def put_detail_client(
    id_client: int,
    client_update: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_admin_permission(current_user)
    
    client = db.get(Client, id_client)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    try:
        update_data = client_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(client, key, value)

        db.commit()
        return client
    
    except HTTPException as e:
        raise
    
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dados inválidos"
        )
    
    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar clientes"
        )
    
    except Exception as e:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )


@client_router.delete(
    "/{id_client}",
    response_model=ClientResponse,
    summary="Excluir cliente",
    responses={404: {"description": "Cliente não encontrado"}}
)
async def delete_detail_client(
    id_client: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_admin_permission(current_user) 
    
    client = db.query(Client).get(id_client)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    if client.orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir clientes com pedidos associados"
        )
    
    try:
        db.delete(client)
        db.commit()
        
        return client

    except HTTPException as e:
        raise 

    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir cliente"
        )
    
    except Exception as e:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )
