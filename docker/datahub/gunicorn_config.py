import multiprocessing
import logging

bind = "0.0.0.0:8000"

# Send access and error logs to stdout
# accesslog = "-"
errorlog = "-"

# Log level (info is usually good for production)
loglevel = "info"

# Capture print statements and logs from subprocesses (e.g., Flask app logs)
capture_output = False

# One worker per core (or slightly more if low CPU load)
workers = round(multiprocessing.cpu_count() / 2)

# Type of worker ('sync', 'gthread')
worker_class = "gthread"  # default = 'sync'

# [if 'sync' workers] Limit concurrent connections per worker (helps avoid overload)
# worker_connections = 1000

# [if 'gthread' workers] Number of threads per worker - allows concurrency without needing more processes
threads = 3

# Allow long-running requests (e.g., large POSTs)
timeout = 120  # Keep this unless you notice timeouts under load

# Prevent memory leaks by recycling workers
max_requests = 500  # Lower = less RAM bloat, but more churn
max_requests_jitter = 100  # Add randomness to avoid sync restarts


# Enable keep-alive to reduce connection churn
keepalive = 5  # seconds


def when_ready(server):
    server.log.info(
        f"🚀 Gunicorn starting with {server.cfg.workers} workers, {server.cfg.threads} threads per worker"
    )
