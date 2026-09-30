"""
URLs de la aplicación eventos.

Aquí conectamos las rutas HTTP con las vistas
correspondientes.
"""

from django.urls import path

from .views import (
    EventoListCreateView,
    EventoDetailView,
    RecintoListCreateView,
    SectorListCreateView,
    SectorDetailView,
)


urlpatterns = [

    # --------------------------------------------------------
    # LISTAR Y CREAR EVENTOS
    # --------------------------------------------------------
    #
    # GET:
    #   Público. Admite filtros, búsqueda y orden.
    #
    # POST:
    #   ORGANIZADOR.
    path(
        "",
        EventoListCreateView.as_view(),
        name="eventos-lista-crear",
    ),

    # --------------------------------------------------------
    # DETALLE / MODIFICACIÓN / ELIMINACIÓN
    # --------------------------------------------------------
    #
    # GET:
    #   Público.
    #
    # PUT/PATCH/DELETE:
    #   ORGANIZADOR propietario.
    path(
        "<int:pk>/",
        EventoDetailView.as_view(),
        name="evento-detalle",
    ),

    # --------------------------------------------------------
    # SECTORES DE UN EVENTO
    # --------------------------------------------------------
    #
    # GET:
    #   Público. Admite filtros de precio y disponibilidad.
    #
    # POST:
    #   ORGANIZADOR propietario del evento.
    path(
        "<int:pk>/sectores/",
        SectorListCreateView.as_view(),
        name="evento-sectores",
    ),

    # --------------------------------------------------------
    # GESTIÓN DE INVENTARIO DE UN SECTOR
    # --------------------------------------------------------
    #
    # GET:
    #   Público.
    #
    # PUT/PATCH/DELETE (precio, stock):
    #   ORGANIZADOR propietario del evento.
    path(
        "sectores/<int:pk>/",
        SectorDetailView.as_view(),
        name="sector-detalle",
    ),

    # --------------------------------------------------------
    # RECINTOS
    # --------------------------------------------------------
    #
    # GET:
    #   Público.
    #
    # POST:
    #   ORGANIZADOR.
    path(
        "recintos/",
        RecintoListCreateView.as_view(),
        name="recintos",
    ),
]
