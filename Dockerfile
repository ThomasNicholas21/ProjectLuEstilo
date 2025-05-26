FROM python:3.11-slim

WORKDIR /app

COPY /src /app/src
COPY scripts /scripts
COPY requirements.txt .
COPY alembic alembic
COPY alembic.ini .


RUN apt-get update && apt-get install -y netcat-openbsd \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && chmod -R +x /scripts

ENV PATH="/scripts:/venv/bin:$PATH"

ENV PYTHONPATH=/app

CMD ["startup.sh"]
