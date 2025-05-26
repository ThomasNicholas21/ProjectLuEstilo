from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..common.config import settings


Base = declarative_base()


engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_engine():
    engine.connect()
