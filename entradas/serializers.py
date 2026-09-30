"""
Serializers de la aplicación entradas.

Estos serializers convierten las entradas almacenadas
en PostgreSQL a información JSON para la API.
"""

from rest_framework import serializers

from .models import Entrada


class EntradaSerializer(serializers.ModelSerializer):
    """
    Representa una entrada individual.

    La entrada contiene un UUID único, la compra asociada,
    el sector y su estado de utilización. Además incluye los
    datos del evento necesarios para dibujar el ticket
    (nombre, fecha, recinto y afiche).
    """

    # --------------------------------------------------------
    # DATOS DEL EVENTO (recorren Entrada -> Sector -> Evento)
    # --------------------------------------------------------

    evento = serializers.CharField(
        source="sector.evento.nombre",
        read_only=True
    )

    evento_id = serializers.IntegerField(
        source="sector.evento_id",
        read_only=True
    )

    evento_fecha = serializers.DateTimeField(
        source="sector.evento.fecha",
        read_only=True
    )

    recinto = serializers.CharField(
        source="sector.evento.recinto.nombre",
        read_only=True
    )

    categoria = serializers.CharField(
        source="sector.evento.categoria",
        read_only=True
    )

    imagen = serializers.ImageField(
        source="sector.evento.imagen",
        read_only=True
    )

    sector_nombre = serializers.CharField(
        source="sector.nombre",
        read_only=True
    )

    class Meta:
        model = Entrada

        fields = [
            "id",
            "compra",
            "evento",
            "evento_id",
            "evento_fecha",
            "recinto",
            "categoria",
            "imagen",
            "sector_nombre",
            "creada_en",
            "utilizada",
        ]

        # Todos estos valores son generados por el backend.
        read_only_fields = fields
