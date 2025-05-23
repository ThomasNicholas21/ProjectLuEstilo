from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import relationship
from src.common.database import Base

class Product(Base):
    __tablename__ = "product"

    id_product = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    name = Column(String(100), nullable=False)
    bar_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    valid_date = Column(DateTime, nullable=True)
    images = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    section = Column(String(50), nullable=True)

    order_items = relationship("OrderItem", back_populates="product")
