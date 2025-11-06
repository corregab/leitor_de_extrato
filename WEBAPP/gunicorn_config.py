"""Configuração do Gunicorn para produção."""

import os

# Bind na porta fornecida pelo Render (ou 5000 como fallback)
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Workers (processos)
workers = 2

# Threads por worker
threads = 2

# Timeout (em segundos)
timeout = 120

# Tipo de worker
worker_class = 'sync'

# Log
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Reload em produção (desabilitado)
reload = False
