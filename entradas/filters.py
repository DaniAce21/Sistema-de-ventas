"""
Filtros de la aplicación entradas (django-filter).

Ejemplos:

    GET /api/mis-entradas/?evento=2
    GET /api/mis-entradas/?utilizada=false
"""

import django_filters

from .models import Entrada


class EntradaFilter(django_filters.FilterSet):
    """
    Filtros de las entradas del espectador.
    """

    # Entradas de un evento específico (Entrada -> Sector -> Evento).
    evento = django_filters.NumberFilter(
        field_name="sector__evento_id",
    )

    # ?utilizada=false  ->  entradas que aún no se usan en el acceso.
    utilizada = django_filters.BooleanFilter()

    class Meta:
        model = Entrada
        fields = [
            "evento",
            "utilizada",
        ]
