FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./radius_api .

RUN chmod +x entrypoint.sh

EXPOSE 8010

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--config", "gunicorn_config.py", "radius_api.wsgi:application"]
