"""
URLs de la aplicación carrito.

Estas rutas permiten consultar, modificar y eliminar
elementos del carrito persistente.
"""

from django.urls import path

from .views import (
    CarritoView,
    EliminarItemCarritoView,
)


urlpatterns = [
    # GET    -> consultar el carrito.
    # POST   -> agregar un sector.
    # DELETE -> quitar un sector o vaciar el carrito.
    path(
        "",
        CarritoView.as_view(),
        name="carrito"
    ),

    # Eliminar un item específico del carrito por su ID.
    path(
        "item/<int:pk>/",
        EliminarItemCarritoView.as_view(),
        name="carrito-eliminar"
    ),
]
