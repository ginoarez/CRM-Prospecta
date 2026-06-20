FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
    libffi-dev libcairo2 shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
