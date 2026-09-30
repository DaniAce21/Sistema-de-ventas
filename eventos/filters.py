"""
Filtros de la aplicación eventos (django-filter).

Un FilterSet traduce parámetros de la URL (query params)
en condiciones sobre el QuerySet, sin escribir SQL a mano.

Ejemplos:

    GET /api/eventos/?categoria=CONCIERTO
    GET /api/eventos/?fecha_desde=2026-10-01&fecha_hasta=2026-12-31
    GET /api/eventos/?precio_max=30000&con_stock=true
    GET /api/eventos/{id}/sectores/?precio_min=10000&disponible=true
"""

import django_filters

from .models import Evento, Sector


class EventoFilter(django_filters.FilterSet):
    """
    Filtros del catálogo público de eventos.
    """

    # --------------------------------------------------------
    # FILTROS SOBRE CAMPOS DEL EVENTO
    # --------------------------------------------------------

    # Búsqueda parcial sin distinguir mayúsculas:
    # ?nombre=rock  ->  WHERE nombre ILIKE '%rock%'
    nombre = django_filters.CharFilter(
        field_name="nombre",
        lookup_expr="icontains",
    )

    # Filtra por los valores definidos en Evento.Estado (CHOICES).
    # Un valor fuera de las opciones devuelve 400.
    # (El público solo ve PROGRAMADOS; el filtro sirve al organizador.)
    estado = django_filters.ChoiceFilter(
        choices=Evento.Estado.choices,
    )

    # Filtra por los valores definidos en Evento.Categoria (CHOICES):
    # ?categoria=TEATRO
    categoria = django_filters.ChoiceFilter(
        choices=Evento.Categoria.choices,
    )

    # ?recinto=3  ->  eventos realizados en el recinto con id 3.
    recinto = django_filters.NumberFilter(
        field_name="recinto_id",
    )

    # Rango de fechas (se compara solo la parte de fecha).
    fecha_desde = django_filters.DateFilter(
        field_name="fecha",
        lookup_expr="date__gte",
    )

    fecha_hasta = django_filters.DateFilter(
        field_name="fecha",
        lookup_expr="date__lte",
    )

    # --------------------------------------------------------
    # FILTROS SOBRE LOS SECTORES DEL EVENTO
    # --------------------------------------------------------
    #
    # El precio y el stock están en Sector, no en Evento.
    # Usamos una subconsulta (pk__in) para obtener los eventos
    # que tienen al menos un sector que cumple la condición,
    # sin generar filas duplicadas por el JOIN.
    #

    # Eventos con alguna entrada desde este precio.
    precio_min = django_filters.NumberFilter(
        method="filtrar_precio_min",
    )

    # Eventos con alguna entrada hasta este precio.
    precio_max = django_filters.NumberFilter(
        method="filtrar_precio_max",
    )

    # ?con_stock=true  ->  eventos con al menos un sector disponible.
    con_stock = django_filters.BooleanFilter(
        method="filtrar_con_stock",
    )

    class Meta:
        model = Evento
        fields = [
            "nombre",
            "estado",
            "categoria",
            "recinto",
            "fecha_desde",
            "fecha_hasta",
            "precio_min",
            "precio_max",
            "con_stock",
        ]

    @staticmethod
    def _eventos_con_sectores(queryset, **condiciones):
        """
        Devuelve los eventos que tienen al menos un sector
        que cumple las condiciones indicadas.
        """

        eventos_ids = Sector.objects.filter(
            **condiciones
        ).values("evento_id")

        return queryset.filter(pk__in=eventos_ids)

    def filtrar_precio_min(self, queryset, name, value):
        return self._eventos_con_sectores(queryset, precio__gte=value)

    def filtrar_precio_max(self, queryset, name, value):
        return self._eventos_con_sectores(queryset, precio__lte=value)

    def filtrar_con_stock(self, queryset, name, value):
        """
        true  -> eventos con algún sector con stock.
        false -> eventos completamente agotados.
        """

        con_stock = self._eventos_con_sectores(queryset, stock__gt=0)

        if value:
            return con_stock

        return queryset.exclude(pk__in=con_stock.values("pk"))


class SectorFilter(django_filters.FilterSet):
    """
    Filtros de los sectores de un evento.
    """

    # Rango de precios: ?precio_min=10000&precio_max=50000
    precio_min = django_filters.NumberFilter(
        field_name="precio",
        lookup_expr="gte",
    )

    precio_max = django_filters.NumberFilter(
        field_name="precio",
        lookup_expr="lte",
    )

    # ?disponible=true  ->  solo sectores con stock mayor a 0.
    disponible = django_filters.BooleanFilter(
        method="filtrar_disponible",
    )

    class Meta:
        model = Sector
        fields = [
            "precio_min",
            "precio_max",
            "disponible",
        ]

    def filtrar_disponible(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)

        return queryset.filter(stock=0)
