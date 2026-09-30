"""
Modelos de la aplicación compras.

Aquí almacenamos el historial de las compras realizadas
por los usuarios.

Una compra es independiente del carrito.

El carrito representa lo que el usuario desea comprar,
mientras que la compra representa una operación histórica
que ya fue procesada.
"""

from django.db import models

from usuarios.models import Usuario


class Compra(models.Model):
    """
    Representa una compra realizada por un usuario.

    Una vez creada, esta información permanece almacenada
    como historial aunque posteriormente el usuario
    modifique su carrito.
    """

    class Estado(models.TextChoices):
        """
        Estados permitidos para una compra.

        PENDIENTE:
        La compra todavía no ha sido pagada.

        PAGADO:
        El pago fue procesado y el stock fue descontado.

        ENTREGADO:
        Las entradas fueron entregadas/utilizadas
        según el flujo definido por el sistema.

        CANCELADO:
        La compra fue cancelada y, si correspondía,
        el stock debe ser restaurado.
        """

        PENDIENTE = "PENDIENTE", "Pendiente"
        PAGADO = "PAGADO", "Pagado"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="compras",
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Compra #{self.id} - {self.usuario.username}"


class ItemCompra(models.Model):
    """
    Representa una línea histórica de una compra.

    Guardamos el nombre, precio y cantidad que existían
    al momento de realizar la compra.

    Esto es importante porque el precio de un sector
    podría cambiar posteriormente, pero el historial
    de la compra no debe cambiar.
    """

    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name="items",
    )

    sector = models.ForeignKey(
        "eventos.Sector",
        on_delete=models.PROTECT,
        related_name="items_comprados",
    )

    cantidad = models.PositiveIntegerField()

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    def __str__(self):
        return (
            f"Compra #{self.compra.id} - "
            f"{self.sector.nombre} x {self.cantidad}"
        )