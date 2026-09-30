"""
Configuración WSGI del proyecto venta_entradas.

WSGI es la interfaz estándar entre un servidor web de Python
(Gunicorn, mod_wsgi, etc.) y Django. En producción el servidor
importa la variable "application" definida aquí.

Documentación:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Indica a Django qué archivo de configuración utilizar.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'venta_entradas.settings')

application = get_wsgi_application()
