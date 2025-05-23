# src/routers/client.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.common.database import get_db
from src.clients.models import Client
from src.clients.serializer import ClientCreate, ClientUpdate, ClientResponse


client_router = APIRouter(prefix="/clients", tags=["Clients"])


@client_router.post("/", response_model=ClientResponse)
async def post_client(client: ClientCreate, db: Session = Depends(get_db)):
    try:
        db_client = Client(**client.__dict__)
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    
    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {e}")


@client_router.get("/", response_model=list[ClientResponse])
async def get_client(db: Session = Depends(get_db)):
    try:
        response = db.query(Client).all()
        return response

    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {e}")


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
