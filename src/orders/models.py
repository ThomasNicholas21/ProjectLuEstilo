from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from src.common.database import Base
from enum import Enum as PyEnum

class OrderStatus(PyEnum):
    PENDING = "pendente"
    PROCESSING = "processando"
    COMPLETED = "finalizado"
    CANCELLED = "cancelado"
    

class Order(Base):
    __tablename__ = "order"

    id_order = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client = Column(Integer, ForeignKey('client.id_client'), nullable=False)
    total_amount = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    client_rel = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
