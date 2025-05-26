from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.common.config import settings, init_sentry
from src.common.database import create_db_engine
from src.clients.routers import client_router
from src.auth.routers import auth_router
from src.products.routers import product_router
from src.orders.routers import order_router
from src.utils.exceptions import sentry_exception_middleware, register_exception_handlers
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_engine()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0", 
    lifespan=lifespan
)


init_sentry()


app.include_router(client_router)
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(order_router)

app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sentry_exception_middleware(app)
register_exception_handlers(app)
