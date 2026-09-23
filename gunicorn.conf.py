"""
Configuracion profesional de Gunicorn para multi-usuario.
Colocar junto a app.py o referencia en Procfile.
"""
import multiprocessing
import os

# Bind
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Workers: 2-4x CPU cores. En Render free tier con 512MB, 2 es optimo.
workers = min(2, multiprocessing.cpu_count() + 1)

# Threads por worker: para I/O-bound (llamadas a APIs externas)
threads = 4

# Worker class
worker_class = "gthread"

# Timeout para requests lentos (TTS, LLM, etc.)
timeout = 120

# Keep-alive para conexiones persistentes
keepalive = 5

# Reciclar workers despues de N requests (evitar memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
