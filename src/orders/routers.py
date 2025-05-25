from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    Query, 
    status)
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime, timezone
from src.common.database import get_db
from src.auth.security.token import get_current_user
from src.orders.models import Order, OrderItem
from src.products.models import Product
from src.clients.models import Client
from src.orders.schemas import OrderCreate, OrderResponse, OrderUpdate
from src.utils.role_validator import check_admin_permission


order_router = APIRouter(
    prefix="/orders",
    tags=["Pedidos"],
    responses={
        403: {"description": "Acesso negado"},
        401: {"description": "Credenciais inválidas"},
        404: {"description": "Recurso não encontrado"}
    }
)


@order_router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo pedido",
    responses={
        400: {"description": "Estoque insuficiente ou dados inválidos"},
        404: {"description": "Produto não encontrado"}
    }
)
async def post_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_admin_permission(current_user)
    
    try:
        total_price = 0
        total_amount = 0
        order_items = []

        for item in order.products:
            product = db.query(Product).get(item.id_product)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Produto ID {item.id_product} não encontrado"
                )

            if product.stock < item.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para {product.name} (ID {product.id_product})"
                )

            product.stock -= item.amount
            total_price += product.price * item.amount
            total_amount += item.amount

            order_items.append(OrderItem(
                id_product=item.id_product,
                amount=item.amount,
                unit_price=product.price
            ))

        new_order = Order(
            id_client=order.id_client,
            status=order.status,
            total_amount=total_amount,
            total_price=total_price,
            created_at=datetime.now(timezone.utc),
            items=order_items
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order

    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar pedido no banco de dados"
        )
    
    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar pedido."
        )


@order_router.get(
    "/",
    response_model=List[OrderResponse],
    summary="Listar pedidos com filtros",
    responses={200: {"description": "Lista de pedidos paginada"}}
)
async def get_order(
    id_order: Optional[int] = Query(None, example=1, description="Filtrar por ID do pedido"),
    id_product: Optional[int] = Query(None, example=1, description="Filtrar por ID do produto"),
    id_client: Optional[int] = Query(None, example=1, description="Filtrar por ID do cliente"),
    status: Optional[str] = Query(None, example="pendente", description="Status do pedido"),
    section: Optional[str] = Query(None, example="eletrônicos", description="Seção dos produtos"),
    start_date: Optional[datetime] = Query(None, example="2024-01-01T00:00:00Z", description="Data inicial"),
    end_date: Optional[datetime] = Query(None, example="2024-12-31T23:59:59Z", description="Data final"),
    skip: int = Query(0, ge=0, example=0),
    limit: int = Query(10, ge=1, le=100, example=10),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        query = db.query(Order)

        if id_order:
            query = query.filter(Order.id_order == id_order)

        if id_client:
            query = query.filter(Order.id_client == id_client)

        if status:
            query = query.filter(Order.status == status)

        if section:
            query = query.join(Order.items).join(OrderItem.product).filter(Product.section.ilike(f"%{section}%"))

        if id_product:
            query = query.join(Order.items).filter(OrderItem.id_product == id_product)

        if start_date and end_date:
            query = query.filter(Order.created_at.between(start_date, end_date))

        elif start_date:
            query = query.filter(Order.created_at >= start_date)

        elif end_date:
            query = query.filter(Order.created_at <= end_date)

        return query.offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao consultar banco de dados"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar pedido."
        )


@order_router.get(
    "/{id_order}",
    response_model=OrderResponse,
    summary="Detalhes de um pedido",
    responses={404: {"description": "Pedido não encontrado"}}
)
async def get_detail_order(
    id_order: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try: 
        order = db.query(Order).get(id_order)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido ID {id_order} não encontrado"
            )
        return order
    
    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao consultar banco de dados"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar pedido."
        )


@order_router.put("/{id_order}", response_model=OrderResponse)
async def put_detail_order(id_order: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    try:
        order = db.query(Order).get(id_order)
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")

        update_data = order_update.model_dump(exclude_unset=True)

        if "id_client" in update_data:
            new_client = db.query(Client).filter(Client.id_client == update_data["id_client"]).first()
            if not new_client:
                raise HTTPException(
                    status_code=404,
                    detail=f"Cliente ID {update_data['id_client']} não encontrado"
                )
            order.id_client = update_data["id_client"]

        if "status" in update_data:
            order.status = update_data["status"]

        if "products" in update_data and update_data["products"]:
            for item in order.items:
                db.delete(item)
            db.flush()

            total_price = 0
            total_amount = 0
            new_items = []

            for item_data in update_data["products"]:
                product = db.query(Product).filter(Product.id_product == item_data.id_product).first()
                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Produto ID {item_data.id_product} não encontrado"
                    )

                if product.stock < item_data.amount:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Estoque insuficiente para o produto ID {item_data.id_product}"
                    )

                product.stock -= item_data.amount
                db.add(product)

                total_price += product.price * item_data.amount
                total_amount += item_data.amount

                order_item = OrderItem(
                    id_product=item_data.id_product,
                    amount=item_data.amount,
                    unit_price=product.price,
                    order=order
                )
                new_items.append(order_item)

            order.items = new_items
            order.total_price = total_price
            order.total_amount = total_amount

        db.commit()
        db.refresh(order)
        return order

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {e}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar pedido: {str(e)}")
    


@order_router.delete("{id_order}", response_model=OrderResponse)
async def delete_detail_order(id_order: str, db: Session = Depends(get_db)):
    try:
        order = db.query(Order).get(id_order)

        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado.")
        
        db.delete(order)
        db.commit()
        
        return order

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {e}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar pedido: {str(e)}")
    
