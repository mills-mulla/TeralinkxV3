# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for Pillow and PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set Django settings module (optional override via docker-compose)
ENV DJANGO_SETTINGS_MODULE=teralinkx.settings

# Expose port
EXPOSE 8000

# Gunicorn entrypoint
CMD ["gunicorn", "--config", "gunicorn_config.py", "teralinkx.wsgi:application"]
