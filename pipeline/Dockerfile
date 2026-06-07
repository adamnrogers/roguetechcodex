FROM python:3.11-slim

WORKDIR /app

COPY pipeline/ ./pipeline/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["python", "-m", "pipeline.ingest", "--full-rebuild"]
