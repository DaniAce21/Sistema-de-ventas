"""
Modelos de la aplicación usuarios.

En esta aplicación definimos el usuario personalizado
del sistema y los roles que tendrá cada usuario.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario personalizado del sistema.

    Heredamos de AbstractUser para conservar las funciones
    de autenticación que Django ya proporciona, como:

    - username
    - password
    - email
    - first_name
    - last_name
    - is_staff
    - is_active

    Además agregamos el campo "rol", que utilizaremos
    posteriormente para implementar permisos RBAC.
    """

    class Rol(models.TextChoices):
        """
        Define los roles disponibles dentro del sistema.

        ESPECTADOR:
        Puede consultar eventos, utilizar el carro,
        comprar entradas y consultar sus propias entradas.

        ORGANIZADOR:
        Puede administrar sus eventos y realizar
        operaciones de gestión autorizadas.
        """

        ESPECTADOR = "ESPECTADOR", "Espectador"
        ORGANIZADOR = "ORGANIZADOR", "Organizador"

    # --------------------------------------------------------
    # ROL DEL USUARIO
    # --------------------------------------------------------
    #
    # El campo utiliza choices para limitar los valores
    # permitidos a los roles definidos anteriormente.
    #
    # Además, la pauta exige explícitamente el uso de
    # CHOICES dentro de los modelos.
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.ESPECTADOR,
    )

    def __str__(self):
        """
        Representación legible del usuario.

        Django utilizará este método cuando necesite
        mostrar el usuario como texto.
        """
        return self.username