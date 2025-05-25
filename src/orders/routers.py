from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime
from src.common.database import get_db
from src.orders.models import Order, OrderItem
from src.products.models import Product
from src.orders.serializer import OrderCreate, OrderResponse


order_router = APIRouter(prefix="/orders", tags=["Orders"])


@order_router.post("/", response_model=OrderResponse)
async def post_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        total_price = 0
        total_amount = 0
        order_items: List[OrderItem] = []

        for item in order.products:
            product = db.query(Product).filter(Product.id_product == item.id_product).first()

            if not product:
                raise HTTPException(status_code=404, detail=f"Produto ID {item.id_product} não encontrado")

            if product.stock < item.amount:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente para o produto ID {item.id_product}"
                )

            product.stock -= item.amount
            db.add(product)

            item_total_price = product.price * item.amount
            total_price += item_total_price
            total_amount += item.amount

            order_item = OrderItem(
                id_product=item.id_product,
                amount=item.amount,
                unit_price=product.price  
            )
            order_items.append(order_item)

        new_order = Order(
            id_client=order.id_client,
            status=order.status,
            total_amount=total_amount,
            total_price=total_price,
            created_at=datetime.utcnow(),
            items=order_items
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order

    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro ao criar pedido: {e}")

    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


@order_router.get("/", response_model=List[OrderResponse])
async def get_order(
    id_order: Optional[int] = Query(default=None),
    id_product: Optional[int] = Query(default=None),
    id_client: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    section: Optional[str] = Query(default=None),
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Order)

        if section:
            query = query.join(Order.items).join(OrderItem.product).filter(Product.section.ilike(f"%{section}%"))

        if id_order:
            query = query.filter(Order.id_order == id_order)

        if id_product:
            query = query.join(Order.items).join(OrderItem.product).filter(Product.id_product == id_product)


        if id_client:
            query = query.filter(Order.id_client == id_client)

        if status:
            query = query.filter(Order.status == status)

        if start_date and end_date:
            query = query.filter(Order.created_at.between(start_date, end_date))

        elif start_date:
            query = query.filter(Order.created_at >= start_date)

        elif end_date:
            query = query.filter(Order.created_at <= end_date)

        orders = query.offset(skip).limit(limit).all()
        return orders

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pedidos: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")
