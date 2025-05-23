import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Adiciona o caminho do projeto para permitir importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa Base e models
from src.common.database import Base
from src.clients.models import Client
from src.orders.models import Order
from src.common.config import settings

# Configuração base do Alembic
config = context.config

# Substitui a URL do banco no alembic.ini pelo valor do .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configuração de logging (opcional, mas recomendada)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define os metadados que o Alembic vai usar para autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa as migrations no modo offline (sem engine)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa as migrations no modo online (com engine real)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True  # importante: detecta alterações de tipo de coluna
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
