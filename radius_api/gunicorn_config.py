import os
from prometheus_client import Gauge

# Use environment variable for port, default to 8001 for RADIUS API
port = os.getenv('RADIUS_API_PORT', '8001')
bind = f"0.0.0.0:{port}"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# Prometheus metrics
worker_gauge = Gauge('gunicorn_workers', 'Number of Gunicorn workers', ['state'])

def child_exit(server, worker):
    worker_gauge.labels(state='active').dec()

def post_fork(server, worker):
    worker_gauge.labels(state='active').inc()

def when_ready(server):
    worker_gauge.labels(state='active').set(workers)

print(f"🚀 Starting RADIUS API Gunicorn with {workers} workers on {bind}")
print(f"📊 Log level: {loglevel}")
