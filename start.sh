#!/bin/bash
# Configuracion multi-usuario para TusAbogados.com
# 2 workers + 4 threads = 8 conexiones simultaneas
gunicorn app:app \
  --config gunicorn.conf.py \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --threads 4 \
  --timeout 120 \
  --keep-alive 5
