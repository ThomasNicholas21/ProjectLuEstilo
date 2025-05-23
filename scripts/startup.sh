#!/bin/bash

until nc -z lu_estilo_db 5432; do
    echo "Postegre iniciando..."
    sleep 1
done

# Aplica migrations ao subir
alembic upgrade head

# Start the application
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
