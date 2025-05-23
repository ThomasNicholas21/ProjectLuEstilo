from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lu Estilo API"
    DATABASE_URL: str

    class Config:
        env_file = "dotenv/.env"

settings = Settings()
