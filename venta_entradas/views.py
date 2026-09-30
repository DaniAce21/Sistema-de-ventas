"""
Vistas generales del proyecto:

1. Datos del alumno para el footer del frontend.
2. Documentación OpenAPI / Swagger protegida por RBAC.

Documentación:

La documentación solo es accesible para usuarios con rol
de gestión (ORGANIZADOR o ADMIN).

Como el navegador no envía el header "Authorization: Bearer"
al abrir /api/docs/, estas vistas aceptan además la sesión
de Django (login en /api-auth/login/).

- Sin autenticar      -> redirección al login.
- Autenticado sin rol -> 403 Forbidden.
"""

from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from usuarios.permissions import IsGestor


# ============================================================
# DATOS DEL ALUMNO
# ============================================================

class AlumnoView(APIView):
    """
    GET /api/alumno/

    Devuelve nombre, sección y año definidos en settings.ALUMNO.
    Es público porque el footer se muestra a todos los visitantes.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        responses=inline_serializer(
            name="Alumno",
            fields={
                "nombre": serializers.CharField(),
                "seccion": serializers.CharField(),
                "anio": serializers.IntegerField(),
            },
        ),
    )
    def get(self, request):
        return Response(settings.ALUMNO)


# ============================================================
# DOCUMENTACIÓN OPENAPI / SWAGGER
# ============================================================


class DocsProtegidasMixin:
    """
    Autenticación y permisos compartidos por el esquema
    y la interfaz Swagger.
    """

    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsGestor]


class SchemaProtegidoView(DocsProtegidasMixin, SpectacularAPIView):
    """
    GET /api/schema/

    Esquema OpenAPI en formato YAML/JSON.
    """


class SwaggerProtegidoView(DocsProtegidasMixin, SpectacularSwaggerView):
    """
    GET /api/docs/

    Interfaz Swagger UI.
    """

    def handle_exception(self, exc):
        """
        Si el visitante no ha iniciado sesión, lo enviamos
        al login y luego de vuelta a la documentación.
        """

        if isinstance(exc, NotAuthenticated):
            login_url = reverse("rest_framework:login")
            query = urlencode({"next": self.request.get_full_path()})

            return HttpResponseRedirect(f"{login_url}?{query}")

        return super().handle_exception(exc)
