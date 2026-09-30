"""
Configuración de la aplicación carrito.
"""

from django.apps import AppConfig


class CarritoConfig(AppConfig):
    """
    Configuración principal de la aplicación carrito.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "carrito"

    def ready(self):
        """
        Importamos los signals cuando Django termina
        de cargar la aplicación.

        Esto permite que Django registre automáticamente
        nuestra función de creación de carritos.
        """

        import carrito.signals