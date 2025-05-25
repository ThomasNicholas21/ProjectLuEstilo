from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime
from src.common.database import get_db
from src.orders.models import Order, OrderItem
from src.products.models import Product
from src.orders.serializer import OrderCreate, OrderResponse


order_router = APIRouter(prefix="/orders", tags=["Orders"])


@order_router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
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
