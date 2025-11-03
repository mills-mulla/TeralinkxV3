import multiprocessing

bind = "0.0.0.0:8000"
workers = 5                  # 2 cores -> (2*2)+1
worker_class = "gthread"     
threads = 4                  # I/O-bound tasks
max_requests = 1000
max_requests_jitter = 50
timeout = 60                 # per request max
keepalive = 30               # keep idle connections alive longer
backlog = 2048               # request queue
accesslog = "-"
errorlog = "-"
preload_app = True           # optional: load Django before forking
