import multiprocessing

bind = "0.0.0.0:8000"

workers = multiprocessing.cpu_count() + 1

log_file = "-"

# Consider "gthread" or "uvicorn.workers.UvicornWorker" only if using async frameworks (e.g., FastAPI)
worker_class = "sync"  # Explicit is better than implicit

# Allow long-running requests (e.g., large POSTs)
timeout = 120  # Keep this unless you notice timeouts under load

# Prevent memory leaks by recycling workers
max_requests = 500  # Lower = less RAM bloat, but more churn
max_requests_jitter = 100  # Add randomness to avoid sync restarts

# Limit concurrent connections per worker (helps avoid overload)
worker_connections = 1000  # Default for "sync", can be tuned

# Enable keep-alive to reduce connection churn
keepalive = 5  # seconds
