"""
Serializers de la aplicación carrito.

Los serializers se encargan de transformar los modelos
de Django en información JSON para nuestra API.

También validan los datos que recibe el backend antes
de modificar el carrito.
"""

from rest_framework import serializers

from .models import Carrito, ItemCarrito
from eventos.models import Evento, Sector


class SectorCarritoSerializer(serializers.ModelSerializer):
    """
    Serializer reducido de un sector.

    Lo utilizamos para mostrar dentro del carrito
    la información necesaria del sector seleccionado.
    """

    evento = serializers.CharField(
        source="evento.nombre",
        read_only=True
    )

    # Datos extra para mostrar el item como en la ficha del evento.
    evento_id = serializers.IntegerField(
        source="evento.id",
        read_only=True
    )

    evento_fecha = serializers.DateTimeField(
        source="evento.fecha",
        read_only=True
    )

    imagen = serializers.ImageField(
        source="evento.imagen",
        read_only=True
    )

    categoria = serializers.CharField(
        source="evento.categoria",
        read_only=True
    )

    class Meta:
        model = Sector
        fields = [
            "id",
            "evento",
            "evento_id",
            "evento_fecha",
            "imagen",
            "categoria",
            "nombre",
            "precio",
            "stock",
        ]


class ItemCarritoSerializer(serializers.ModelSerializer):
    """
    Serializer de cada producto/sector agregado al carrito.

    El sector se muestra como información de solo lectura.
    La cantidad sí puede ser modificada mediante la API.
    """

    sector = SectorCarritoSerializer(read_only=True)

    class Meta:
        model = ItemCarrito
        fields = [
            "id",
            "sector",
            "cantidad",
            "creado_en",
        ]


class CarritoSerializer(serializers.ModelSerializer):
    """
    Serializer principal del carrito.

    Incluye todos los items pertenecientes
    al carrito del usuario autenticado.
    """

    items = ItemCarritoSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Carrito
        fields = [
            "id",
            "usuario",
            "items",
            "creado_en",
            "actualizado_en",
        ]

        # El usuario no debe poder cambiar el propietario
        # de su carrito mediante una petición HTTP.
        read_only_fields = [
            "usuario",
            "creado_en",
            "actualizado_en",
        ]


class AgregarItemCarritoSerializer(serializers.Serializer):
    """
    Serializer utilizado cuando el espectador
    quiere agregar un sector a su carrito.

    Recibimos solamente:

        sector_id
        cantidad

    El carrito se obtiene automáticamente a partir
    del usuario autenticado.
    """

    sector_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)

    def validate_sector_id(self, value):
        """
        Comprueba que el sector indicado exista.

        No descontamos stock aquí.

        La validación definitiva del stock se realizará
        durante el proceso de pago, porque ese es el
        momento en que la compra se convierte en una
        operación transaccional.
        """

        sector = (
            Sector.objects
            .select_related("evento")
            .filter(id=value)
            .first()
        )

        if sector is None:
            raise serializers.ValidationError(
                "El sector seleccionado no existe."
            )

        # No tiene sentido reservar entradas de un evento
        # que ya finalizó o fue cancelado.
        if sector.evento.estado != Evento.Estado.PROGRAMADO:
            raise serializers.ValidationError(
                "El evento de este sector no está disponible para la venta."
            )

        return value


class EliminarItemCarritoSerializer(serializers.Serializer):
    """
    Serializer utilizado en DELETE /api/carro-tickets/.

    - Con sector_id: elimina ese sector del carrito.
    - Sin sector_id: vacía el carrito completo.
    """

    sector_id = serializers.IntegerField(
        required=False
    )