"""
URLs de la aplicación entradas.
"""

from django.urls import path

from .views import MisEntradasView


urlpatterns = [
    # Entradas pertenecientes al usuario autenticado.
    path(
        "mis-entradas/",
        MisEntradasView.as_view(),
        name="mis-entradas",
    ),
]