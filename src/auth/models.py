from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from src.common.database import Base
from enum import Enum as PyEnum


class UserRole(PyEnum):
    ADMIN = "admin"
    STAFF = "regular"


class User(Base):
    __tablename__ = "user"

    id_user = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(SqlEnum(UserRole), nullable=False)
