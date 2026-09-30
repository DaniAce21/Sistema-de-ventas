"""
URLs relacionadas con la autenticación.

Aquí definimos los endpoints para obtener y renovar
los tokens JWT.
"""

from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginTokenView, PerfilView, RegistroView


urlpatterns = [
    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------
    #
    # POST /api/auth/token/
    #
    # Recibe username + password y devuelve:
    # access + refresh.
    path(
        "token/",
        LoginTokenView.as_view(),
        name="token-obtain",
    ),

    # --------------------------------------------------------
    # REFRESH TOKEN
    # --------------------------------------------------------
    #
    # POST /api/auth/token/refresh/
    #
    # Permite obtener un nuevo access token utilizando
    # un refresh token válido.
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    # --------------------------------------------------------
    # REGISTRO DE ESPECTADORES
    # --------------------------------------------------------
    #
    # POST /api/auth/registro/
    #
    # Público. Crea siempre un usuario con rol ESPECTADOR.
    path(
        "registro/",
        RegistroView.as_view(),
        name="registro",
    ),

    # --------------------------------------------------------
    # PERFIL
    # --------------------------------------------------------
    #
    # GET/PATCH /api/auth/perfil/
    #
    # Datos del usuario autenticado.
    path(
        "perfil/",
        PerfilView.as_view(),
        name="perfil",
    ),
]