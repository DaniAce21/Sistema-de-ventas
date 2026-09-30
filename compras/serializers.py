"""
Serializers de la aplicación compras.

Estos serializers permiten representar las compras
y sus elementos en formato JSON.

También utilizaremos un serializer específico para
solicitar el proceso de pago.
"""

from rest_framework import serializers

from .models import Compra, ItemCompra


class ItemCompraSerializer(serializers.ModelSerializer):
    """
    Representa una línea de una compra.

    Muestra la información histórica de lo comprado,
    incluyendo cantidad, precio unitario y subtotal.
    """

    sector = serializers.StringRelatedField()

    class Meta:
        model = ItemCompra
        fields = [
            "id",
            "sector",
            "cantidad",
            "precio_unitario",
            "subtotal",
        ]


class CompraSerializer(serializers.ModelSerializer):
    """
    Representa una compra completa.

    Incluye sus elementos históricos.
    """

    items = ItemCompraSerializer(
        many=True,
        read_only=True
    )

    # Mostramos el nombre del comprador en lugar de su ID.
    usuario = serializers.CharField(
        source="usuario.username",
        read_only=True
    )

    class Meta:
        model = Compra
        fields = [
            "id",
            "usuario",
            "estado",
            "total",
            "items",
            "creado_en",
            "actualizado_en",
        ]

        # Estos campos son generados por el backend.
        # El cliente no puede modificarlos directamente.
        read_only_fields = [
            "usuario",
            "estado",
            "total",
            "items",
            "creado_en",
            "actualizado_en",
        ]


class PagarCompraSerializer(serializers.Serializer):
    """
    Serializer utilizado para iniciar el proceso de pago.

    Actualmente no necesitamos recibir información
    adicional desde el frontend.

    El backend obtiene automáticamente el carrito
    perteneciente al usuario autenticado.
    """

    confirmar = serializers.BooleanField(
        default=True
    )

    def validate_confirmar(self, value):
        """
        Verifica que el usuario haya confirmado
        la intención de realizar el pago.
        """

        if value is not True:
            raise serializers.ValidationError(
                "Debe confirmar el pago."
            )

        return value

class CambiarEstadoCompraSerializer(serializers.Serializer):
    """
    Serializer utilizado por un organizador para cambiar
    el estado de una compra.

    El estado recibido será validado antes de ejecutar
    cualquier modificación en la base de datos.
    """

    estado = serializers.ChoiceField(
        choices=Compra.Estado.choices
    )