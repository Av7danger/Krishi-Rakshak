FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc ffmpeg && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
RUN pip install --upgrade pip && pip install -e .[dev]

COPY krishirakshak_backend /app/krishirakshak_backend

ENV APP_ENV=production

EXPOSE 8000
CMD ["uvicorn", "krishirakshak_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
