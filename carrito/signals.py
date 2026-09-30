"""
Signals de la aplicación carrito.

Los signals permiten ejecutar lógica automáticamente
cuando ocurre un evento dentro de Django.

En este caso crearemos un carrito automáticamente
cada vez que se cree un usuario.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from usuarios.models import Usuario

from .models import Carrito


@receiver(post_save, sender=Usuario)
def crear_carrito_usuario(sender, instance, created, **kwargs):
    """
    Crea automáticamente un carrito cuando se registra
    un usuario nuevo.

    Esto garantiza que cada usuario tenga un carrito
    persistente asociado mediante la relación OneToOne.
    """

    if created:
        Carrito.objects.create(usuario=instance)