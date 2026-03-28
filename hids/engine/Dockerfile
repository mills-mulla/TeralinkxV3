FROM python:3.11-slim

WORKDIR /app

# Install netcat and redis-tools for health checks
RUN apt-get update && apt-get install -y netcat-openbsd redis-tools && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "engine.py"]
