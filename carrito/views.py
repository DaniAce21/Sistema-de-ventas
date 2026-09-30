"""
Vistas de la aplicación carrito.

Aquí implementamos las operaciones que puede realizar
un espectador sobre su carrito:

- Consultar su carrito.
- Agregar sectores.
- Eliminar sectores.

El carrito pertenece exclusivamente al usuario autenticado.
"""

from django.db.models import F

from drf_spectacular.utils import extend_schema

from rest_framework import generics, status
from rest_framework.response import Response

from usuarios.permissions import IsEspectador

from .models import Carrito, ItemCarrito
from .serializers import (
    CarritoSerializer,
    ItemCarritoSerializer,
    AgregarItemCarritoSerializer,
    EliminarItemCarritoSerializer,
)


def obtener_carrito(usuario):
    """
    Obtiene el carrito del usuario, creándolo si no existe.

    El signal ya crea el carrito al registrar el usuario,
    pero get_or_create cubre usuarios creados antes del signal.
    """

    carrito, _ = Carrito.objects.get_or_create(
        usuario=usuario
    )

    return carrito


def respuesta_carrito(carrito, status_code=status.HTTP_200_OK):
    """
    Devuelve el carrito actualizado, con sus items y sectores.
    """

    carrito = (
        Carrito.objects
        .prefetch_related("items__sector__evento")
        .get(pk=carrito.pk)
    )

    return Response(
        CarritoSerializer(carrito).data,
        status=status_code,
    )


class CarritoView(generics.GenericAPIView):
    """
    Carro persistente del usuario autenticado.

        GET    /api/carro-tickets/   Consultar el carrito.
        POST   /api/carro-tickets/   Agregar un sector.
        DELETE /api/carro-tickets/   Quitar un sector o vaciar el carrito.

    IMPORTANTE:

    Nunca buscamos el carrito mediante un ID enviado
    por el frontend. Lo buscamos utilizando request.user,
    de modo que un usuario no puede operar sobre
    el carrito de otra persona.

    Ninguna de estas operaciones modifica el stock.
    El stock se valida y descuenta en el checkout.
    """

    permission_classes = [IsEspectador]
    serializer_class = CarritoSerializer

    def get(self, request):
        """
        Devuelve el carrito con todos sus items.
        """

        return respuesta_carrito(
            obtener_carrito(request.user)
        )

    @extend_schema(
        request=AgregarItemCarritoSerializer,
        responses={201: CarritoSerializer},
    )
    def post(self, request):
        """
        Agrega un sector al carrito.

        Si el sector ya está en el carrito, aumentamos
        la cantidad en lugar de crear un registro duplicado.
        """

        serializer = AgregarItemCarritoSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        sector_id = serializer.validated_data["sector_id"]
        cantidad = serializer.validated_data["cantidad"]

        carrito = obtener_carrito(request.user)

        item, item_created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            sector_id=sector_id,
            defaults={
                "cantidad": cantidad
            }
        )

        if not item_created:
            # Si el sector ya estaba en el carrito, sumamos
            # la cantidad con F() para que la actualización
            # ocurra en la base de datos y no se pierdan
            # incrementos de peticiones simultáneas.
            #
            # Todavía NO modificamos el stock del sector.
            ItemCarrito.objects.filter(pk=item.pk).update(
                cantidad=F("cantidad") + cantidad
            )

        return respuesta_carrito(
            carrito,
            status_code=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=EliminarItemCarritoSerializer,
        responses={200: CarritoSerializer},
    )
    def delete(self, request):
        """
        Elimina items del carrito.

        Body opcional:

            {"sector_id": 3}  -> quita ese sector.
            {}                -> vacía el carrito.
        """

        serializer = EliminarItemCarritoSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        carrito = obtener_carrito(request.user)
        sector_id = serializer.validated_data.get("sector_id")

        items = carrito.items.all()

        if sector_id is not None:
            items = items.filter(sector_id=sector_id)

            if not items.exists():
                return Response(
                    {"error": "Ese sector no está en el carrito."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        items.delete()

        return respuesta_carrito(carrito)


class EliminarItemCarritoView(generics.DestroyAPIView):
    """
    Elimina un item específico del carrito por su ID.

        DELETE /api/carro-tickets/item/{id}/

    La consulta se limita al carrito del usuario autenticado,
    evitando que pueda eliminar elementos pertenecientes
    a otro usuario.
    """

    permission_classes = [IsEspectador]
    serializer_class = ItemCarritoSerializer

    def get_queryset(self):
        """
        Retorna únicamente los items pertenecientes
        al carrito del usuario actual.
        """

        # drf-spectacular inspecciona la vista sin usuario real.
        if getattr(self, "swagger_fake_view", False):
            return ItemCarrito.objects.none()

        return ItemCarrito.objects.filter(
            carrito__usuario=self.request.user
        )
