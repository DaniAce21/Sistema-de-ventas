"""
Configuración de la aplicación compras.
"""

from django.apps import AppConfig


class ComprasConfig(AppConfig):
    """
    Aplicación de órdenes: checkout transaccional,
    estados de la compra y reposición de stock.
    """

    # Tipo de clave primaria por defecto de los modelos de la app.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compras'
