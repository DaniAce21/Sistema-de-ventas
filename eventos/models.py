"""
Modelos de la aplicación eventos.

En este archivo definimos las entidades relacionadas
con los eventos, recintos y sectores/localidades.

La estructura será:

Recinto
   └── Evento
          └── Sector

De esta manera podemos representar que un evento
se realiza en un recinto y que cada evento posee
diferentes sectores con precios y cantidades de entradas.
"""

from django.db import models

from usuarios.models import Usuario


class Recinto(models.Model):
    """
    Representa el lugar físico donde se realizará un evento.

    Ejemplos:
    - Estadio Municipal
    - Teatro Municipal
    - Arena
    """

    # --------------------------------------------------------
    # INFORMACIÓN BÁSICA DEL RECINTO
    # --------------------------------------------------------

    nombre = models.CharField(
        max_length=150
    )

    direccion = models.CharField(
        max_length=250
    )

    def __str__(self):
        """
        Devuelve el nombre del recinto cuando Django
        necesita representarlo como texto.
        """
        return self.nombre


class Evento(models.Model):
    """
    Representa un evento o concierto disponible
    para la venta de entradas.
    """

    # --------------------------------------------------------
    # ESTADOS DEL EVENTO
    # --------------------------------------------------------
    #
    # Utilizamos TextChoices para limitar los estados
    # permitidos dentro de la base de datos.
    #
    # Esto también cumple con el requisito de la pauta
    # relacionado con el uso de CHOICES.
    class Estado(models.TextChoices):
        PROGRAMADO = "PROGRAMADO", "Programado"
        FINALIZADO = "FINALIZADO", "Finalizado"
        CANCELADO = "CANCELADO", "Cancelado"

    # --------------------------------------------------------
    # CATEGORÍAS DEL EVENTO
    # --------------------------------------------------------
    #
    # Segundo campo con CHOICES. Permite agrupar el catálogo
    # y filtrarlo: GET /api/eventos/?categoria=CONCIERTO
    #
    class Categoria(models.TextChoices):
        CONCIERTO = "CONCIERTO", "Conciertos"
        FESTIVAL = "FESTIVAL", "Festivales"
        TEATRO = "TEATRO", "Teatro"
        STANDUP = "STANDUP", "Stand-up"
        DEPORTE = "DEPORTE", "Deportes"
        FAMILIAR = "FAMILIAR", "Familiar"
        OTRO = "OTRO", "Otros"

    # --------------------------------------------------------
    # INFORMACIÓN DEL EVENTO
    # --------------------------------------------------------

    nombre = models.CharField(
        max_length=200
    )

    descripcion = models.TextField(
        blank=True
    )

    fecha = models.DateTimeField()

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PROGRAMADO
    )

    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.CONCIERTO
    )

    # --------------------------------------------------------
    # AFICHE DEL EVENTO
    # --------------------------------------------------------
    #
    # ImageField valida que el archivo sea una imagen (Pillow).
    # El archivo se guarda en MEDIA_ROOT/eventos/ y en la base
    # de datos solo se almacena su ruta relativa.
    #
    imagen = models.ImageField(
        upload_to="eventos/",
        blank=True,
        null=True
    )

    # --------------------------------------------------------
    # RELACIÓN CON EL RECINTO
    # --------------------------------------------------------
    #
    # Cada evento pertenece a un recinto.
    #
    # Si un recinto es eliminado, sus eventos también
    # serán eliminados mediante CASCADE.
    recinto = models.ForeignKey(
        Recinto,
        on_delete=models.CASCADE,
        related_name="eventos"
    )

    # --------------------------------------------------------
    # RELACIÓN CON EL ORGANIZADOR
    # --------------------------------------------------------
    #
    # Cada evento queda asociado al usuario que lo creó.
    #
    # Posteriormente utilizaremos esta relación para que
    # un ORGANIZADOR solamente pueda administrar sus propios
    # eventos.
    organizador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="eventos"
    )

    def __str__(self):
        """
        Devuelve el nombre del evento.
        """
        return self.nombre


class Sector(models.Model):
    """
    Representa una localidad o sector dentro de un evento.

    Ejemplos:
    - Cancha
    - Galería
    - VIP
    - Platea

    Cada sector tiene su propio precio y stock.
    """

    # --------------------------------------------------------
    # RELACIÓN CON EL EVENTO
    # --------------------------------------------------------
    #
    # Un evento puede tener varios sectores.
    #
    # Por ejemplo:
    #
    # Concierto X
    # ├── VIP
    # ├── Cancha
    # └── Galería
    #
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name="sectores"
    )

    # --------------------------------------------------------
    # DATOS DEL SECTOR
    # --------------------------------------------------------

    nombre = models.CharField(
        max_length=100
    )

    # Precio de una entrada perteneciente a este sector.
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Cantidad total/disponible de entradas del sector.
    stock = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        """
        Devuelve una representación legible del sector.
        """
        return f"{self.evento.nombre} - {self.nombre}"