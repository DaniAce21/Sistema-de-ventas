
"""
URLs principales del proyecto.

Este archivo funciona como punto de entrada para
las diferentes aplicaciones de nuestra API.

Aquí conectamos:

- Panel administrativo de Django.
- Autenticación JWT.
- API de eventos.
- API del carrito.
- API de compras.
- API de entradas.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from .views import AlumnoView, SchemaProtegidoView, SwaggerProtegidoView


# Títulos del panel /admin/ (se muestran en su cabecera y pestaña).
admin.site.site_header = "Butaca · Administración"
admin.site.site_title = "Butaca"
admin.site.index_title = "Gestión del sistema de venta de entradas"


urlpatterns = [

    # --------------------------------------------------------
    # PORTADA DEL BACKEND
    # --------------------------------------------------------
    #
    # Página HTML con accesos a la documentación, al panel
    # /admin/ y al frontend. Plantilla: templates/inicio.html
    #
    path(
        "",
        TemplateView.as_view(template_name="inicio.html"),
        name="inicio",
    ),

    # --------------------------------------------------------
    # DATOS DEL ALUMNO
    # --------------------------------------------------------
    #
    # Público. El frontend los muestra en su footer.
    #
    # GET /api/alumno/
    #
    path(
        "api/alumno/",
        AlumnoView.as_view(),
        name="alumno",
    ),

    # --------------------------------------------------------
    # DOCUMENTACIÓN OPENAPI / SWAGGER
    # --------------------------------------------------------
    #
    # Restringida por RBAC a ORGANIZADOR / ADMIN.
    #
    # GET /api/schema/
    # GET /api/docs/
    #
    path(
        "api/schema/",
        SchemaProtegidoView.as_view(),
        name="schema",
    ),
    path(
        "api/docs/",
        SwaggerProtegidoView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # Login por sesión para acceder a /api/docs/ desde el navegador.
    path(
        "api-auth/",
        include("rest_framework.urls"),
    ),


    # --------------------------------------------------------
    # PANEL ADMINISTRATIVO
    # --------------------------------------------------------
    #
    # Permite administrar usuarios, eventos, sectores,
    # recintos y demás información desde Django Admin.
    #
    path(
        "admin/",
        admin.site.urls
    ),

    # --------------------------------------------------------
    # AUTENTICACIÓN
    # --------------------------------------------------------
    #
    # Incluye los endpoints para obtener y renovar
    # los tokens JWT.
    #
    # POST /api/auth/token/
    # POST /api/auth/token/refresh/
    #
    path(
        "api/auth/",
        include("usuarios.urls")
    ),

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------
    #
    # Incluye los endpoints públicos para consultar
    # eventos y sectores, además de las operaciones
    # autorizadas para organizadores.
    #
    # GET    /api/eventos/
    # GET    /api/eventos/{id}/
    # GET    /api/eventos/{id}/sectores/
    #
    path(
        "api/eventos/",
        include("eventos.urls")
    ),

    # --------------------------------------------------------
    # CARRITO
    # --------------------------------------------------------
    #
    # API del carrito persistente del usuario.
    #
    # GET    /api/carro-tickets/
    # POST   /api/carro-tickets/
    # DELETE /api/carro-tickets/
    # DELETE /api/carro-tickets/item/{id}/
    #
    path(
        "api/carro-tickets/",
        include("carrito.urls")
    ),

    # --------------------------------------------------------
    # COMPRAS
    # --------------------------------------------------------
    #
    # Incluye el proceso de pago y el cambio de estado
    # de las compras.
    #
    # GET   /api/compras/
    # GET   /api/compras/resumen/
    # POST  /api/compras/pagar/
    # PATCH /api/compras/{id}/estado/
    #
    path(
        "api/compras/",
        include("compras.urls")
    ),

    # --------------------------------------------------------
    # ENTRADAS
    # --------------------------------------------------------
    #
    # Permite al espectador consultar sus entradas
    # generadas después de una compra.
    #
    # GET /api/mis-entradas/
    #
    path(
        "api/",
        include("entradas.urls")
    ),
]


# ------------------------------------------------------------
# ARCHIVOS SUBIDOS (AFICHES)
# ------------------------------------------------------------
#
# En desarrollo Django sirve los archivos de MEDIA_ROOT.
# En producción esta tarea corresponde al servidor web (Nginx).
#
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

