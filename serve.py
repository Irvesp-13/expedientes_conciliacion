"""
Script de arranque de produccion para Waitress en Windows.

Uso:
    venv\Scripts\activate
    python serve.py

Equivalente a:
    waitress-serve --host=0.0.0.0 --port=8000 expedientes_conciliacion.wsgi:application

Se usa este archivo (en lugar de waitress-serve directo) para poder ajustar
facilmente el numero de hilos (threads) y el tiempo de espera (timeout).
"""

import os

from waitress import serve
from expedientes_conciliacion.wsgi import application

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))

    print(f"Iniciando expedientes_conciliacion en http://{host}:{port}")

    serve(
        application,
        host=host,
        port=port,
        threads=8,
        channel_timeout=120,
        cleanup_interval=30,
        max_request_body_size=104857600,
    )
