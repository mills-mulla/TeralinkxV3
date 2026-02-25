import multiprocessing
import os

# Calculate optimal workers based on CPU cores
cpu_count = multiprocessing.cpu_count()
workers = min(max((cpu_count * 2) + 1, 3), 8)  # 3-8 workers range

bind = "0.0.0.0:8009"  # V3 port
worker_class = "gthread"
threads = 4

# Worker recycling - CRITICAL for preventing memory leaks
max_requests = 200  # Reduced from 1000 - recycle workers faster
max_requests_jitter = 50  # Add randomness to prevent thundering herd

# Timeouts
timeout = 30  # Reduced from 60 - kill slow requests faster
graceful_timeout = 30  # Time for graceful worker shutdown
keepalive = 5  # Reduced from 30 - close idle connections faster

# Connection settings
backlog = 2048
worker_connections = 1000

# Memory optimization
worker_tmp_dir = "/dev/shm"  # Use RAM for temp files
preload_app = True  # Load app before forking workers

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

print(f"Starting Gunicorn with {workers} workers on {bind}")
print(f"Worker recycling: max_requests={max_requests}, jitter={max_requests_jitter}")
print(f"Timeout: {timeout}s, Keepalive: {keepalive}s")
