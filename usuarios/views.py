"""
Vistas relacionadas con la autenticación de usuarios.

En este archivo conectamos nuestro serializer personalizado
con las vistas proporcionadas por SimpleJWT, y agregamos
el registro público de espectadores y el perfil del usuario.
"""

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LoginTokenSerializer, PerfilSerializer, RegistroSerializer


class LoginTokenView(TokenObtainPairView):
    """
    Endpoint para iniciar sesión y obtener los tokens JWT.

    Método:

        POST /api/auth/token/

    El usuario debe enviar sus credenciales.

    La respuesta contendrá:

    - access
    - refresh

    Además, el JWT incluirá el rol del usuario.
    """

    # Utilizamos nuestro serializer personalizado
    # para agregar el campo "rol" al JWT.
    serializer_class = LoginTokenSerializer


class RegistroView(generics.CreateAPIView):
    """
    Registro público de espectadores.

        POST /api/auth/registro/

    Body:
        {"username", "email", "password", "first_name", "last_name"}

    El rol siempre es ESPECTADOR (ver RegistroSerializer).
    """

    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]

    # Sin autenticación: un token vencido en el navegador
    # no debe impedir crear una cuenta nueva.
    authentication_classes = []


class PerfilView(generics.RetrieveUpdateAPIView):
    """
    Perfil del usuario autenticado.

        GET   /api/auth/perfil/   Ver datos.
        PATCH /api/auth/perfil/   Editar nombre y correo.

    Siempre opera sobre request.user: no recibe un ID por URL,
    por lo que nadie puede ver ni editar el perfil de otro.
    """

    serializer_class = PerfilSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
