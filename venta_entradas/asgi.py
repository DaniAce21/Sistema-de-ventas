"""
Configuración ASGI del proyecto venta_entradas.

ASGI es la versión asíncrona de WSGI (servidores como Uvicorn o
Daphne). Se incluye por defecto en Django aunque este proyecto
se ejecute con WSGI.

Documentación:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Indica a Django qué archivo de configuración utilizar.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'venta_entradas.settings')

application = get_asgi_application()
