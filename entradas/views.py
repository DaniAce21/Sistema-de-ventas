"""
Vistas de la aplicación entradas.

Aquí implementamos la consulta de las entradas
pertenecientes al usuario autenticado.
"""

from rest_framework import generics

from compras.models import Compra
from usuarios.permissions import IsEspectador

from .filters import EntradaFilter
from .models import Entrada
from .serializers import EntradaSerializer


class MisEntradasView(generics.ListAPIView):
    """
    Devuelve exclusivamente las entradas del usuario
    autenticado.

    Un usuario nunca puede consultar las entradas
    pertenecientes a otra cuenta.
    """

    serializer_class = EntradaSerializer
    permission_classes = [IsEspectador]

    # Filtros: ?evento=2  ?utilizada=false  (ver entradas/filters.py)
    filterset_class = EntradaFilter

    def get_queryset(self):
        """
        Filtra las entradas utilizando el propietario
        de la compra asociada.

        De esta forma aplicamos aislamiento de datos
        entre usuarios.

        Las entradas de compras CANCELADAS dejan de ser
        válidas, por lo que no se muestran.
        """

        # drf-spectacular inspecciona la vista sin usuario real.
        if getattr(self, "swagger_fake_view", False):
            return Entrada.objects.none()

        return (
            Entrada.objects
            .select_related(
                "compra",
                "sector",
                "sector__evento",
                "sector__evento__recinto",
            )
            .filter(
                compra__usuario=self.request.user,
                compra__estado__in=[
                    Compra.Estado.PAGADO,
                    Compra.Estado.ENTREGADO,
                ],
            )
            .order_by("-creada_en")
        )