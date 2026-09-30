#!/bin/bash
# Configuracion multi-usuario para TusAbogados.com
# 1 worker (obligatorio: las sesiones viven en memoria del proceso)
# + 4 threads = 4 conexiones simultaneas I/O-bound
gunicorn app:app \
  --config gunicorn.conf.py \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --threads 4 \
  --timeout 120 \
  --keep-alive 5
