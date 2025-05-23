from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.common.database import Base

class OrderItem(Base):
    __tablename__ = "orderitem"

    id_orderitem = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_order = Column(Integer, ForeignKey("order.id_order"), nullable=False)
    id_product = Column(Integer, ForeignKey("product.id_product"), nullable=False)
    amount = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
