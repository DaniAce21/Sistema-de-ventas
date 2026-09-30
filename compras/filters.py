"""
Filtros de la aplicación compras (django-filter).

Ejemplos:

    GET /api/compras/?estado=PAGADO
    GET /api/compras/?evento=2&fecha_desde=2026-10-01
"""

import django_filters

from .models import Compra


class CompraFilter(django_filters.FilterSet):
    """
    Filtros del listado de compras.
    """

    # Filtra por los estados definidos en Compra.Estado (CHOICES).
    estado = django_filters.ChoiceFilter(
        choices=Compra.Estado.choices,
    )

    # Compras que incluyen entradas de un evento específico.
    # Recorre la relación Compra -> ItemCompra -> Sector -> Evento.
    # distinct=True evita repetir una compra con varios items del evento.
    evento = django_filters.NumberFilter(
        field_name="items__sector__evento_id",
        distinct=True,
    )

    # Rango de fechas de creación de la compra.
    fecha_desde = django_filters.DateFilter(
        field_name="creado_en",
        lookup_expr="date__gte",
    )

    fecha_hasta = django_filters.DateFilter(
        field_name="creado_en",
        lookup_expr="date__lte",
    )

    class Meta:
        model = Compra
        fields = [
            "estado",
            "evento",
            "fecha_desde",
            "fecha_hasta",
        ]
