from prometheus_client import Gauge

bind = "0.0.0.0:8010"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Prometheus metrics
worker_gauge = Gauge('gunicorn_workers', 'Number of Gunicorn workers', ['state'])

def child_exit(server, worker):
    worker_gauge.labels(state='active').dec()

def post_fork(server, worker):
    worker_gauge.labels(state='active').inc()

def when_ready(server):
    worker_gauge.labels(state='active').set(workers)
