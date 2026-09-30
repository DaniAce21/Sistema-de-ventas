"""
Serializers relacionados con la autenticación.

Aquí personalizamos el JWT de SimpleJWT para agregar
información propia de nuestro sistema, específicamente
el rol del usuario.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Usuario


class LoginTokenSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para generar JWT.

    SimpleJWT genera normalmente dos tokens:

    - Access token:
      Se utiliza para acceder a los endpoints protegidos.

    - Refresh token:
      Permite obtener un nuevo access token cuando
      el anterior expira.

    Además agregaremos el rol del usuario dentro
    del payload del JWT.
    """

    @classmethod
    def get_token(cls, user):
        """
        Obtiene el token estándar generado por SimpleJWT
        y agrega información adicional de nuestro sistema.
        """

        # ----------------------------------------------------
        # GENERAR TOKEN ESTÁNDAR
        # ----------------------------------------------------
        #
        # Esta llamada conserva toda la funcionalidad
        # original proporcionada por SimpleJWT.
        token = super().get_token(user)

        # ----------------------------------------------------
        # AGREGAR ROL AL PAYLOAD
        # ----------------------------------------------------
        #
        # El rol viajará dentro del JWT y posteriormente
        # podrá ser utilizado por nuestro sistema de permisos.
        token["rol"] = user.rol

        # El frontend lo muestra en la barra de navegación.
        token["username"] = user.username

        return token


class RegistroSerializer(serializers.ModelSerializer):
    """
    Registro público de nuevos espectadores.

    SEGURIDAD:
    El campo "rol" NO se acepta desde el frontend. Todo usuario
    registrado por esta vía es ESPECTADOR; los administradores
    (ORGANIZADOR) solo se crean desde el panel /admin/.
    """

    # write_only: la contraseña nunca se devuelve en la respuesta.
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    email = serializers.EmailField(
        required=True
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]

    def validate_email(self, value):
        """
        Evita dos cuentas con el mismo correo.
        """

        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Ya existe una cuenta con este correo."
            )

        return value.lower()

    def validate(self, attrs):
        """
        Aplica los validadores de contraseña de settings.py
        (largo mínimo, contraseñas comunes, solo números, etc.).
        """

        datos = {k: v for k, v in attrs.items() if k != "password"}

        try:
            validate_password(attrs["password"], user=Usuario(**datos))
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": list(error.messages)})

        return attrs

    def create(self, validated_data):
        """
        create_user() guarda la contraseña con hash (nunca en texto plano)
        y forzamos el rol ESPECTADOR.
        """

        return Usuario.objects.create_user(
            **validated_data,
            rol=Usuario.Rol.ESPECTADOR,
        )


class PerfilSerializer(serializers.ModelSerializer):
    """
    Datos del usuario autenticado (GET /api/auth/perfil/).
    """

    rol_display = serializers.CharField(
        source="get_rol_display",
        read_only=True,
    )

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "rol",
            "rol_display",
        ]
        read_only_fields = [
            "id",
            "username",
            "rol",
        ]