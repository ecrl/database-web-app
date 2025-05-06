import os


workers = int(os.getenv("GUNICORN_PROCESSES", "1"))
threads = int(os.getenv("GUNICORN_THREADS", "1"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}
