import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Lu Estilo API"
    DATABASE_URL: str
    SECRET_KEY: str
    SENTRY_DNS: str
    model_config = ConfigDict(env_file="dotenv/.env")

settings = Settings()


def init_sentry():
    sentry_sdk.init(
        dsn=settings.SENTRY_DNS,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=1.0,  
        environment="development"  
    )
