from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.common.database import Base
from src.orders.models import Order


class Client(Base):
    __tablename__ = "client"

    id_client = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    cpf = Column(String(14), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    
    orders = relationship("Order", back_populates="client")
