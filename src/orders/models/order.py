from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String
from sqlalchemy.orm import relationship
from src.common.database import Base
    

class Order(Base):
    __tablename__ = "order"

    id_order = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_client = Column(Integer, ForeignKey('client.id_client'), nullable=False)
    total_amount = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)
    
    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")
