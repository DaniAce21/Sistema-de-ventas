"""
Configuración administrativa de los usuarios.

Personalizamos el panel de administración de Django
para mostrar también el rol propio de nuestro sistema.

Los roles disponibles son:

- ESPECTADOR
- ORGANIZADOR
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración del usuario personalizado.

    Heredamos de UserAdmin para conservar todas las
    funciones administrativas que Django proporciona
    para los usuarios.

    Además agregamos nuestro campo personalizado "rol".
    """

    # ========================================================
    # CAMPOS MOSTRADOS AL EDITAR UN USUARIO
    # ========================================================
    #
    # Agregamos "rol" dentro de la sección de permisos
    # para poder modificarlo directamente desde el admin.
    #

    fieldsets = UserAdmin.fieldsets + (
        (
            "Información del sistema",
            {
                "fields": (
                    "rol",
                ),
            },
        ),
    )

    # ========================================================
    # CAMPOS MOSTRADOS AL CREAR UN USUARIO
    # ========================================================
    #
    # También mostramos el rol cuando se crea un usuario
    # desde el panel administrativo.
    #

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Información del sistema",
            {
                "fields": (
                    "rol",
                ),
            },
        ),
    )

    # ========================================================
    # LISTADO DE USUARIOS
    # ========================================================
    #
    # Permitimos visualizar el rol directamente en la lista
    # de usuarios del panel administrativo.
    #

    list_display = (
        "username",
        "email",
        "rol",
        "is_staff",
        "is_active",
    )

    # Permite filtrar usuarios rápidamente por rol.

    list_filter = (
        "rol",
        "is_staff",
        "is_active",
    )
