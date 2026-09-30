"""
Serializers de la aplicación eventos.

Los serializers tienen dos responsabilidades principales:

1. Convertir los modelos de Django a JSON para que
   nuestra API pueda devolver información al frontend.

2. Convertir datos recibidos desde el frontend en
   objetos que Django pueda validar y guardar.
"""

from django.utils import timezone

from rest_framework import serializers

from .models import Recinto, Evento, Sector


# Tamaño máximo permitido para el afiche de un evento.
TAMANO_MAXIMO_IMAGEN = 5 * 1024 * 1024  # 5 MB


class RecintoSerializer(serializers.ModelSerializer):
    """
    Serializer para representar los recintos.

    Permite mostrar la información del lugar donde
    se realizará un evento.
    """

    class Meta:
        model = Recinto

        # Campos que serán expuestos por la API.
        fields = [
            "id",
            "nombre",
            "direccion",
        ]


class SectorSerializer(serializers.ModelSerializer):
    """
    Serializer para representar los sectores de un evento.

    Ejemplo de respuesta:

    {
        "id": 1,
        "nombre": "VIP",
        "precio": "50000.00",
        "stock": 100
    }
    """

    class Meta:
        model = Sector

        # Exponemos los datos necesarios para que
        # el cliente pueda consultar disponibilidad
        # y precio de las entradas.
        fields = [
            "id",
            "nombre",
            "precio",
            "stock",
        ]

    def validate_precio(self, value):
        """
        Una entrada no puede tener precio negativo.
        (El stock ya es PositiveIntegerField en el modelo.)
        """

        if value < 0:
            raise serializers.ValidationError(
                "El precio no puede ser negativo."
            )

        return value


class EventoSerializer(serializers.ModelSerializer):
    """
    Serializer principal de los eventos.

    Además de los datos básicos del evento, incluye:

    - El recinto anidado (lectura) y recinto_id (escritura).
    - La etiqueta legible de la categoría y el estado.
    - El afiche como URL absoluta.
    - precio_desde y disponibles: resumen de sus sectores,
      usado por las tarjetas del catálogo ("Desde $20.000").

    Los sectores tienen un endpoint específico:

        GET /api/eventos/{id}/sectores/
    """

    # --------------------------------------------------------
    # RECINTO
    # --------------------------------------------------------
    #
    # Utilizamos otro serializer para representar el recinto
    # directamente dentro de la respuesta del evento.
    recinto = RecintoSerializer(
        read_only=True
    )

    # Campo de escritura: al crear/editar un evento
    # el organizador envía solamente el ID del recinto.
    recinto_id = serializers.PrimaryKeyRelatedField(
        queryset=Recinto.objects.all(),
        source="recinto",
        write_only=True,
    )

    # --------------------------------------------------------
    # ETIQUETAS LEGIBLES DE LOS CHOICES
    # --------------------------------------------------------
    #
    # get_<campo>_display() devuelve la etiqueta del choice:
    # "CONCIERTO" -> "Conciertos".
    categoria_display = serializers.CharField(
        source="get_categoria_display",
        read_only=True,
    )

    estado_display = serializers.CharField(
        source="get_estado_display",
        read_only=True,
    )

    organizador = serializers.CharField(
        source="organizador.username",
        read_only=True,
    )

    # --------------------------------------------------------
    # RESUMEN DE SECTORES
    # --------------------------------------------------------
    precio_desde = serializers.SerializerMethodField()
    disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Evento

        fields = [
            "id",
            "nombre",
            "descripcion",
            "fecha",
            "estado",
            "estado_display",
            "categoria",
            "categoria_display",
            "imagen",
            "recinto",
            "recinto_id",
            "organizador",
            "precio_desde",
            "disponibles",
        ]

    def get_precio_desde(self, obj) -> str | None:
        """
        Precio más bajo entre los sectores del evento.

        La vista lo calcula en la misma consulta SQL con
        annotate(Min(...)). Si el objeto no viene anotado
        (por ejemplo, recién creado) se calcula aquí.
        """

        if hasattr(obj, "precio_desde"):
            valor = obj.precio_desde
        else:
            valor = min(
                (sector.precio for sector in obj.sectores.all()),
                default=None,
            )

        return str(valor) if valor is not None else None

    def get_disponibles(self, obj) -> int:
        """
        Suma del stock de todos los sectores del evento.
        """

        if hasattr(obj, "disponibles"):
            return obj.disponibles or 0

        return sum(sector.stock for sector in obj.sectores.all())

    def validate_imagen(self, value):
        """
        Limita el tamaño del afiche para no saturar el servidor.
        Pillow ya validó que el archivo sea una imagen real.
        """

        if value and value.size > TAMANO_MAXIMO_IMAGEN:
            raise serializers.ValidationError(
                "La imagen no puede superar los 5 MB."
            )

        return value

    def validate_fecha(self, value):
        """
        Un evento nuevo no puede programarse en el pasado.
        Al editar un evento existente se permite (por ejemplo,
        para marcar como FINALIZADO un evento ya realizado).
        """

        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError(
                "La fecha del evento debe ser futura."
            )

        return value
