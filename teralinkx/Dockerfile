FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy and install requirements
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip list | grep gunicorn  # Verify gunicorn is installed

COPY ./teralinkx .
RUN chmod +x entrypoint.sh

ENV DJANGO_SETTINGS_MODULE=teralinkx.settings

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--config", "gunicorn_config.py", "teralinkx.wsgi:application"]