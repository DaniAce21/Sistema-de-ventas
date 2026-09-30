"""
URLs de la aplicación compras.
"""

from django.urls import path

from .views import (
    CompraListView,
    PagarCompraView,
    CambiarEstadoCompraView,
    ResumenOrganizadorView,
)


urlpatterns = [
    # Listar compras (propias o de los eventos del organizador).
    path(
        "",
        CompraListView.as_view(),
        name="compras-lista",
    ),

    # Métricas del dashboard del administrador.
    path(
        "resumen/",
        ResumenOrganizadorView.as_view(),
        name="compras-resumen",
    ),

    # Procesar el pago del carrito.
    path(
        "pagar/",
        PagarCompraView.as_view(),
        name="compras-pagar",
    ),

    # Cambiar el estado de una compra.
    path(
        "<int:pk>/estado/",
        CambiarEstadoCompraView.as_view(),
        name="compra-cambiar-estado",
    ),
]