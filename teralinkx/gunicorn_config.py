import multiprocessing
import os

# Calculate optimal workers based on CPU cores
cpu_count = multiprocessing.cpu_count()
workers = min(max((cpu_count * 2) + 1, 3), 8)  # 3-8 workers range

bind = "0.0.0.0:8009"  # V3 port to avoid V2 conflict
worker_class = "gthread"
threads = 4
max_requests = 1000
max_requests_jitter = 50
timeout = 60
keepalive = 30
backlog = 2048
accesslog = "-"
errorlog = "-"
preload_app = True
worker_connections = 1000

# Memory optimization
max_requests_jitter = 100
worker_tmp_dir = "/dev/shm"  # Use RAM for temp files

# Logging
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

print(f"Starting Gunicorn with {workers} workers on {bind}")
