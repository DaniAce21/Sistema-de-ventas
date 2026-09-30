"""
Configuración de la aplicación entradas.
"""

from django.apps import AppConfig


class EntradasConfig(AppConfig):
    """
    Aplicación de entradas: tickets individuales con código
    UUID generados al pagar una compra.
    """

    # Tipo de clave primaria por defecto de los modelos de la app.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'entradas'
