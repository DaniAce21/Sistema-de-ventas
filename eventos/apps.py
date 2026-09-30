"""
Configuración de la aplicación eventos.
"""

from django.apps import AppConfig


class EventosConfig(AppConfig):
    """
    Aplicación del catálogo: recintos, eventos y sectores
    (precio y stock de cada localidad).
    """

    # Tipo de clave primaria por defecto de los modelos de la app.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eventos'
