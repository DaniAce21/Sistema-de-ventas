"""
Modelos de la aplicación carrito.

El carrito será persistente y estará almacenado
en PostgreSQL.

La estructura será:

Usuario
   │
   │ 1:1
   ▼
Carrito
   │
   │ 1:N
   ▼
ItemCarrito
   │
   ▼
Sector
"""


from django.db import models

from usuarios.models import Usuario
from eventos.models import Sector


class Carrito(models.Model):
    """
    Representa el carrito permanente de un usuario.

    Cada usuario tendrá un único carrito.

    La relación OneToOne garantiza:

        Usuario 1 ───── 1 Carrito
    """

    # --------------------------------------------------------
    # RELACIÓN 1:1 CON EL USUARIO
    # --------------------------------------------------------
    #
    # Un usuario solamente puede tener un carrito.
    #
    # Si el usuario elimina su cuenta, su carrito
    # también será eliminado.
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="carrito",
    )

    # Fecha en que se creó el carrito.
    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    # Fecha de la última modificación.
    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        """
        Representación legible del carrito.
        """
        return f"Carrito de {self.usuario.username}"


class ItemCarrito(models.Model):
    """
    Representa un sector y cantidad seleccionados
    por el usuario.

    Ejemplo:

        Sector: VIP
        Cantidad: 2

    IMPORTANTE:

    Agregar una entrada al carrito NO descuenta stock.

    El stock solamente será descontado cuando la compra
    sea procesada correctamente como PAGADA.
    """

    # --------------------------------------------------------
    # RELACIÓN CON EL CARRITO
    # --------------------------------------------------------
    #
    # Un carrito puede contener varios items.
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name="items",
    )

    # --------------------------------------------------------
    # SECTOR SELECCIONADO
    # --------------------------------------------------------
    #
    # El item apunta al sector específico del evento.
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name="items_carrito",
    )

    # --------------------------------------------------------
    # CANTIDAD
    # --------------------------------------------------------
    #
    # PositiveIntegerField evita cantidades negativas.
    cantidad = models.PositiveIntegerField(
        default=1
    )

    # Fecha en que se agregó el item.
    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        # Un sector aparece una sola vez por carrito.
        # Si el usuario lo agrega de nuevo, se suma la cantidad.
        constraints = [
            models.UniqueConstraint(
                fields=["carrito", "sector"],
                name="unique_sector_por_carrito",
            ),
        ]

    def __str__(self):
        """
        Representación legible del item.
        """
        return (
            f"{self.carrito.usuario.username} - "
            f"{self.sector.nombre} x {self.cantidad}"
        )