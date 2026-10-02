FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/app \
    APP_ENV=production \
    DATABASE_URL=sqlite:////data/production.sqlite3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

RUN addgroup --gid 10001 app && \
    adduser --uid 10001 --gid 10001 --disabled-password --gecos "" app && \
    mkdir -p storage /data && \
    chown -R app:app /app /data

USER app

VOLUME ["/data"]

EXPOSE 3000

CMD ["gunicorn", "main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:3000"]
