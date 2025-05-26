#!/bin/bash
set -e

if [ "$ENVIRONMENT" = "development" ]; then
    echo "⏳ Aguardando banco de dados subir..."
    until nc -z lu_estilo_db 5432; do
        echo "PostgreSQL ainda não está pronto..."
        sleep 1
    done
    echo "✅ Banco de dados está no ar!"
fi

if [ "$ENVIRONMENT" = "production" ]; then
    echo "📦 Aplicando migrations no ambiente de produção..."
    alembic upgrade head
else
    echo "📦 Aplicando migrations no ambiente de desenvolvimento..."
    alembic upgrade head
fi

if [ "$ENVIRONMENT" = "development" ]; then
    echo "🧪 Rodando em modo DEV..."
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "🏁 Rodando em modo PRODUÇÃO..."
    uvicorn src.main:app --host 0.0.0.0 --port 8000
fi
