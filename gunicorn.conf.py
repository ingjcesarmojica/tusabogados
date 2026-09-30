"""
Configuracion profesional de Gunicorn para multi-usuario.
Colocar junto a app.py o referencia en Procfile.
"""
import multiprocessing
import os

# Bind — Render asigna el puerto via variable de entorno PORT
port = os.environ.get('PORT', '10000')
bind = f"0.0.0.0:{port}"

# IMPORTANTE: workers debe ser 1. Las sesiones de chat (ChatSession) se
# guardan en memoria del proceso. Con 2+ workers cada proceso tiene su
# propio diccionario y las peticiones que caen en otro worker pierden el
# estado (el chat vuelve al paso saludo_inicial y valida la descripcion
# como nombre). Con 1 worker + 4 threads la concurrencia I/O-bound se
# mantiene.
workers = 1

# Threads por worker: para I/O-bound (llamadas a APIs externas)
threads = 4

# Worker class
worker_class = "gthread"

# Timeout para requests lentos (TTS, LLM, etc.)
timeout = 120

# Keep-alive para conexiones persistentes
keepalive = 5

# NO reciclar workers: max_requests reinicia el proceso y borra todas las
# sesiones en memoria. Las sesiones se limpian solas por TTL (30 min).
max_requests = 0
max_requests_jitter = 0

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
