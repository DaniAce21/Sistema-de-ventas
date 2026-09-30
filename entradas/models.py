"""
Modelos de la aplicación entradas.

Aquí almacenamos las entradas generadas después
de que una compra es procesada correctamente.

Cada entrada posee un UUID único que permitirá
identificarla individualmente.
"""

import uuid

from django.db import models

from compras.models import Compra
from eventos.models import Sector


class Entrada(models.Model):
    """
    Representa una entrada individual para un evento.

    Cada entrada posee un UUID único.

    Ejemplo:

        550e8400-e29b-41d4-a716-446655440000

    El UUID permite identificar la entrada sin utilizar
    simplemente un número correlativo.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    compra = models.ForeignKey(
        Compra,
        on_delete=models.PROTECT,
        related_name="entradas",
    )

    sector = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        related_name="entradas",
    )

    creada_en = models.DateTimeField(
        auto_now_add=True
    )

    utilizada = models.BooleanField(
        default=False
    )

    def __str__(self):
        return str(self.id)