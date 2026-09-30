"""
Configuración de la aplicación usuarios.
"""

from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    """
    Aplicación de usuarios: modelo Usuario con rol,
    login JWT y permisos RBAC.
    """

    # Tipo de clave primaria por defecto de los modelos de la app.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'
