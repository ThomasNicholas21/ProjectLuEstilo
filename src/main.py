from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.common.config import settings
from src.common.database import create_db_engine
from src.clients.routers import client_router
from src.auth.routers import auth_router
from src.products.routers import product_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_engine()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0", 
    lifespan=lifespan
)

app.include_router(client_router)
app.include_router(auth_router)
app.include_router(product_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def read_root():
    return {
        "message": f"{settings.PROJECT_NAME} testando server"
        }
