"""
Permisos personalizados del sistema.

En este archivo implementamos RBAC
(Role-Based Access Control).

La autorización se realizará utilizando
el campo "rol" almacenado en nuestro usuario.

Matriz de roles:

    Endpoint                          Público  ESPECTADOR  ORGANIZADOR  ADMIN
    GET  /api/eventos/                   ✔         ✔           ✔          ✔
    POST /api/eventos/                                          ✔
    /api/carro-tickets/                            ✔
    POST /api/compras/pagar/                       ✔
    GET  /api/mis-entradas/                        ✔
    PATCH /api/compras/{id}/estado/                             ✔
    /api/docs/ y /api/schema/                                   ✔          ✔
"""

from rest_framework.permissions import BasePermission

from .models import Usuario


class IsEspectador(BasePermission):
    """
    Permite el acceso solamente a usuarios
    cuyo rol sea ESPECTADOR.
    """

    message = "Esta acción está reservada para usuarios con rol ESPECTADOR."

    def has_permission(self, request, view):
        """
        Verifica que el usuario esté autenticado
        y tenga el rol ESPECTADOR.
        """

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == Usuario.Rol.ESPECTADOR
        )


class IsOrganizador(BasePermission):
    """
    Permite el acceso solamente a usuarios
    cuyo rol sea ORGANIZADOR.
    """

    message = "Esta acción está reservada para usuarios con rol ORGANIZADOR."

    def has_permission(self, request, view):
        """
        Verifica que el usuario esté autenticado
        y tenga el rol ORGANIZADOR.
        """

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == Usuario.Rol.ORGANIZADOR
        )


class IsGestor(BasePermission):
    """
    Permite el acceso a usuarios con rol de gestión:

    - ORGANIZADOR.
    - ADMIN (superusuario de Django).

    Se utiliza para proteger la documentación Swagger.
    """

    message = "La documentación solo está disponible para ORGANIZADOR o ADMIN."

    def has_permission(self, request, view):
        """
        Verifica que el usuario esté autenticado y sea
        ORGANIZADOR o superusuario.
        """

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.rol == Usuario.Rol.ORGANIZADOR
                or user.is_superuser
            )
        )
