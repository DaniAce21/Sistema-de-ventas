"""
Vistas de la aplicación compras.

En este archivo implementamos el proceso de checkout
y la modificación del estado de las compras.

Operaciones principales:

1. Procesar el pago de una compra.
2. Validar el stock disponible.
3. Descontar el stock de forma segura.
4. Generar las entradas UUID.
5. Vaciar el carrito después de una compra exitosa.
6. Permitir cambiar el estado de una compra.
7. Restaurar el stock cuando una compra PAGADA
   pasa a estado CANCELADO.
"""

from decimal import Decimal

from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from carrito.models import Carrito
from entradas.models import Entrada
from eventos.models import Evento, Sector
from usuarios.models import Usuario
from usuarios.permissions import IsEspectador, IsOrganizador

from .filters import CompraFilter
from .models import Compra, ItemCompra
from .serializers import (
    CompraSerializer,
    PagarCompraSerializer,
    CambiarEstadoCompraSerializer,
)


# ============================================================
# TRANSICIONES DE ESTADO PERMITIDAS
# ============================================================
#
# Una compra solo pasa a PAGADO mediante el checkout,
# que es el único lugar donde se descuenta stock.
#
# CANCELADO y ENTREGADO son estados finales: si se permitiera
# CANCELADO -> PAGADO, las entradas volverían a ser válidas
# sin haber descontado nuevamente el stock.
#
TRANSICIONES_PERMITIDAS = {
    Compra.Estado.PENDIENTE: {Compra.Estado.CANCELADO},
    Compra.Estado.PAGADO: {Compra.Estado.ENTREGADO, Compra.Estado.CANCELADO},
    Compra.Estado.ENTREGADO: set(),
    Compra.Estado.CANCELADO: set(),
}


def error(mensaje):
    """
    Respuesta 400 con el formato de error del proyecto.
    """

    return Response(
        {"error": mensaje},
        status=status.HTTP_400_BAD_REQUEST,
    )


class CompraListView(generics.ListAPIView):
    """
    GET /api/compras/

    - ESPECTADOR: sus propias compras.
    - ORGANIZADOR: compras que incluyen entradas de sus eventos.

    Filtros (ver compras/filters.py):

        ?estado=PAGADO
        ?evento=2
        ?fecha_desde=2026-10-01&fecha_hasta=2026-10-31
        ?ordering=-total
    """

    serializer_class = CompraSerializer

    filterset_class = CompraFilter

    ordering_fields = [
        "creado_en",
        "total",
    ]

    def get_queryset(self):
        """
        Filtra las compras según el rol del usuario autenticado.
        """

        # drf-spectacular inspecciona la vista sin usuario real.
        if getattr(self, "swagger_fake_view", False):
            return Compra.objects.none()

        user = self.request.user

        queryset = (
            Compra.objects
            .select_related("usuario")
            .prefetch_related("items__sector__evento")
            .order_by("-creado_en")
        )

        if user.rol == Usuario.Rol.ORGANIZADOR:
            return queryset.filter(
                items__sector__evento__organizador=user
            ).distinct()

        return queryset.filter(usuario=user)


class ResumenOrganizadorView(APIView):
    """
    GET /api/compras/resumen/   (ORGANIZADOR)

    Métricas del dashboard del administrador, calculadas
    solo sobre SUS eventos:

    - Recaudación y entradas vendidas (compras PAGADAS o ENTREGADAS).
    - Cantidad de compras por estado.
    - Detalle por evento: vendidas, recaudado y stock disponible.

    Todo se calcula con agregaciones SQL (Sum, Count) en
    PostgreSQL, sin recorrer registros en Python.
    """

    permission_classes = [IsOrganizador]

    # Estados que representan dinero efectivamente recibido.
    ESTADOS_VENDIDOS = [Compra.Estado.PAGADO, Compra.Estado.ENTREGADO]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        user = request.user

        # ----------------------------------------------------
        # LÍNEAS VENDIDAS DE LOS EVENTOS DEL ORGANIZADOR
        # ----------------------------------------------------
        vendidos = ItemCompra.objects.filter(
            sector__evento__organizador=user,
            compra__estado__in=self.ESTADOS_VENDIDOS,
        )

        totales = vendidos.aggregate(
            recaudado=Sum("subtotal"),
            entradas=Sum("cantidad"),
        )

        # ----------------------------------------------------
        # COMPRAS POR ESTADO
        # ----------------------------------------------------
        # Una compra cuenta una sola vez aunque tenga varios
        # items de eventos del organizador (distinct=True).
        compras_por_estado = {
            fila["estado"]: fila["cantidad"]
            for fila in (
                Compra.objects
                .filter(items__sector__evento__organizador=user)
                .values("estado")
                .annotate(cantidad=Count("id", distinct=True))
            )
        }

        # ----------------------------------------------------
        # DETALLE POR EVENTO
        # ----------------------------------------------------
        # Subconsultas con filtro para no mezclar la suma de
        # stock (sectores) con la suma de ventas (items).
        filtro_vendido = Q(
            sectores__items_comprados__compra__estado__in=self.ESTADOS_VENDIDOS
        )

        eventos = (
            Evento.objects
            .filter(organizador=user)
            .annotate(
                vendidas=Coalesce(
                    Sum("sectores__items_comprados__cantidad", filter=filtro_vendido),
                    0,
                ),
                recaudado=Coalesce(
                    Sum("sectores__items_comprados__subtotal", filter=filtro_vendido),
                    Decimal("0"),
                ),
            )
            .order_by("fecha")
        )

        # El stock se consulta aparte para que el JOIN con las
        # ventas no multiplique la suma.
        stock_por_evento = dict(
            Sector.objects
            .filter(evento__organizador=user)
            .values_list("evento_id")
            .annotate(total=Sum("stock"))
        )

        return Response({
            "recaudado": str(totales["recaudado"] or Decimal("0")),
            "entradas_vendidas": totales["entradas"] or 0,
            "eventos_programados": eventos.filter(
                estado=Evento.Estado.PROGRAMADO
            ).count(),
            "compras_por_estado": {
                estado: compras_por_estado.get(estado, 0)
                for estado in Compra.Estado.values
            },
            "eventos": [
                {
                    "id": evento.id,
                    "nombre": evento.nombre,
                    "fecha": evento.fecha,
                    "estado": evento.estado,
                    "vendidas": evento.vendidas,
                    "recaudado": str(evento.recaudado),
                    "disponibles": stock_por_evento.get(evento.id, 0),
                }
                for evento in eventos
            ],
        })


class PagarCompraView(APIView):
    """
    Procesa el pago del carrito del usuario autenticado.

    El stock solamente se descuenta cuando la compra
    se procesa correctamente como PAGADO.

    Toda la operación se ejecuta dentro de una
    transacción atómica.
    """

    permission_classes = [IsEspectador]

    @extend_schema(
        request=PagarCompraSerializer,
        responses={201: CompraSerializer},
    )
    def post(self, request):
        """
        Ejecuta el proceso completo de checkout.

        Flujo:

        1. Validar la solicitud.
        2. Bloquear el carrito del usuario.
        3. Comprobar que el carrito tenga productos.
        4. Bloquear los sectores involucrados.
        5. Validar el stock.
        6. Crear la compra en estado PENDIENTE.
        7. Crear los items históricos y descontar el stock.
        8. Crear una entrada UUID por cada ticket.
        9. Cambiar la compra a PAGADO.
        10. Vaciar el carrito.

        Si alguna operación falla dentro de la transacción,
        Django realiza automáticamente un rollback.
        """

        # ====================================================
        # VALIDACIÓN DE LA SOLICITUD
        # ====================================================

        serializer = PagarCompraSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        # ====================================================
        # INICIO DE LA TRANSACCIÓN
        # ====================================================
        #
        # transaction.atomic() garantiza que las operaciones
        # de la compra se ejecuten como una sola unidad.
        #
        # Si ocurre un error antes de finalizar,
        # los cambios realizados dentro del bloque
        # serán revertidos.
        #
        with transaction.atomic():

            # ------------------------------------------------
            # OBTENER Y BLOQUEAR EL CARRITO DEL USUARIO
            # ------------------------------------------------
            #
            # Nunca recibimos el usuario desde el frontend.
            # Utilizamos request.user, que corresponde
            # al usuario identificado por el JWT.
            #
            # select_for_update() evita que un doble clic
            # en "Pagar" procese dos veces el mismo carrito:
            # la segunda petición espera a que termine la
            # primera y luego encuentra el carrito vacío.
            #
            carrito = (
                Carrito.objects
                .select_for_update()
                .filter(usuario=request.user)
                .first()
            )

            # Si el usuario no tiene carrito,
            # no podemos realizar la compra.
            if carrito is None:
                return error("El usuario no tiene un carrito.")

            # Leemos los items después de bloquear el carrito
            # para trabajar con su estado definitivo.
            items_carrito = list(
                carrito.items.all()
            )

            # No se puede pagar un carrito vacío.
            if not items_carrito:
                return error("El carrito está vacío.")

            # =================================================
            # BLOQUEO DE LOS SECTORES
            # =================================================
            #
            # select_for_update() bloquea las filas de los
            # sectores mientras dura la transacción.
            #
            # Esto evita que dos compras simultáneas
            # consuman el mismo stock disponible.
            #
            # Ordenamos por id para que todas las transacciones
            # bloqueen en el mismo orden y no se produzcan
            # deadlocks entre compras concurrentes.
            #

            sector_ids = [
                item.sector_id
                for item in items_carrito
            ]

            sectores = {
                sector.id: sector
                for sector in (
                    Sector.objects
                    .select_for_update(of=("self",))
                    .select_related("evento")
                    .filter(id__in=sector_ids)
                    .order_by("id")
                )
            }

            # =================================================
            # VALIDACIÓN DEL STOCK
            # =================================================

            for item in items_carrito:

                sector = sectores.get(
                    item.sector_id
                )

                # El sector podría haber sido eliminado
                # después de haber sido agregado al carrito.
                if sector is None:
                    return error("Uno de los sectores ya no existe.")

                # El evento podría haber sido cancelado o
                # finalizado mientras el item estaba en el carrito.
                if sector.evento.estado != Evento.Estado.PROGRAMADO:
                    return error(
                        f"El evento '{sector.evento.nombre}' "
                        f"ya no está disponible para la venta."
                    )

                # La cantidad solicitada no puede superar
                # el stock disponible.
                if item.cantidad > sector.stock:
                    return error(
                        f"Stock insuficiente para "
                        f"'{sector.nombre}'. "
                        f"Disponible: {sector.stock}. "
                        f"Solicitado: {item.cantidad}."
                    )

            # =================================================
            # CREACIÓN DE LA COMPRA
            # =================================================
            #
            # La orden nace como PENDIENTE y solamente pasa
            # a PAGADO cuando se descontó el stock y se
            # generaron todas las entradas.
            #

            compra = Compra.objects.create(
                usuario=request.user,
                estado=Compra.Estado.PENDIENTE,
            )

            total = Decimal("0.00")
            entradas = []

            # =================================================
            # CREACIÓN DE ITEMS, DESCUENTO DE STOCK Y ENTRADAS
            # =================================================

            for item in items_carrito:

                sector = sectores[
                    item.sector_id
                ]

                subtotal = (
                    sector.precio * item.cantidad
                )

                total += subtotal

                # ---------------------------------------------
                # GUARDAMOS EL HISTORIAL DE LA COMPRA
                # ---------------------------------------------
                #
                # Guardamos el precio del momento de la compra
                # para que el historial no cambie si posteriormente
                # se modifica el precio del sector.
                #

                ItemCompra.objects.create(
                    compra=compra,
                    sector=sector,
                    cantidad=item.cantidad,
                    precio_unitario=sector.precio,
                    subtotal=subtotal,
                )

                # ---------------------------------------------
                # DESCONTAMOS EL STOCK
                # ---------------------------------------------
                #
                # La fila está bloqueada, por lo que el valor
                # leído sigue siendo el vigente.
                #

                sector.stock -= item.cantidad

                sector.save(
                    update_fields=["stock"]
                )

                # ---------------------------------------------
                # PREPARAMOS LAS ENTRADAS
                # ---------------------------------------------
                #
                # Una entrada individual por cada ticket.
                # El UUID se genera con uuid.uuid4() al
                # instanciar cada Entrada (default del modelo).
                #

                entradas.extend(
                    Entrada(compra=compra, sector=sector)
                    for _ in range(item.cantidad)
                )

            # Insertamos todas las entradas en una sola consulta.
            Entrada.objects.bulk_create(entradas)

            # =================================================
            # CONFIRMAR EL PAGO
            # =================================================

            compra.total = total
            compra.estado = Compra.Estado.PAGADO

            compra.save(
                update_fields=[
                    "total",
                    "estado",
                    "actualizado_en",
                ]
            )

            # =================================================
            # VACIAR EL CARRITO
            # =================================================
            #
            # Después de completar correctamente la compra,
            # eliminamos los items del carrito.
            #

            carrito.items.all().delete()

        # ====================================================
        # FIN DE LA TRANSACCIÓN
        # ====================================================

        return Response(
            {
                "mensaje": (
                    "Compra realizada correctamente."
                ),
                "compra": CompraSerializer(
                    compra
                ).data,
                "entradas": [
                    str(entrada.id)
                    for entrada in entradas
                ],
            },
            status=status.HTTP_201_CREATED,
        )


class CambiarEstadoCompraView(APIView):
    """
    Permite a un usuario con rol ORGANIZADOR
    cambiar el estado de una compra que incluya
    entradas de alguno de sus eventos.

    Caso especial:

        PAGADO -> CANCELADO

    Cuando esto ocurre, el stock utilizado por
    la compra vuelve a estar disponible.
    """

    permission_classes = [IsOrganizador]

    @extend_schema(
        request=CambiarEstadoCompraSerializer,
        responses={200: CompraSerializer},
    )
    def patch(self, request, pk):
        """
        Cambia el estado de una compra.

        Si una compra que estaba PAGADA pasa a CANCELADO,
        se restaura el stock correspondiente.

        La operación también utiliza transaction.atomic()
        para mantener la consistencia de los datos.
        """

        # ====================================================
        # VALIDAR EL NUEVO ESTADO
        # ====================================================

        serializer = CambiarEstadoCompraSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        nuevo_estado = serializer.validated_data[
            "estado"
        ]

        # ====================================================
        # INICIO DE LA TRANSACCIÓN
        # ====================================================

        with transaction.atomic():

            # ------------------------------------------------
            # OBTENER Y BLOQUEAR LA COMPRA
            # ------------------------------------------------
            #
            # select_for_update() evita que dos operaciones
            # intenten modificar simultáneamente la misma
            # compra (por ejemplo, restaurar el stock dos veces).
            #

            compra = get_object_or_404(
                Compra.objects.select_for_update(),
                pk=pk,
            )

            # ------------------------------------------------
            # AISLAMIENTO ENTRE ORGANIZADORES
            # ------------------------------------------------
            #
            # Un organizador solo gestiona compras que
            # contienen entradas de sus propios eventos.
            # Respondemos 404 para no revelar compras ajenas.
            #

            es_propietario = compra.items.filter(
                sector__evento__organizador=request.user
            ).exists()

            if not es_propietario:
                return Response(
                    {"error": "Compra no encontrada."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            estado_anterior = compra.estado

            # ------------------------------------------------
            # EVITAR CAMBIOS INNECESARIOS
            # ------------------------------------------------

            if estado_anterior == nuevo_estado:
                return Response(
                    {
                        "mensaje": (
                            "La compra ya se encuentra "
                            "en ese estado."
                        ),
                        "compra": CompraSerializer(compra).data,
                    },
                    status=status.HTTP_200_OK,
                )

            # ------------------------------------------------
            # VALIDAR LA TRANSICIÓN
            # ------------------------------------------------

            if nuevo_estado not in TRANSICIONES_PERMITIDAS[estado_anterior]:
                return error(
                    f"No se puede pasar de {estado_anterior} "
                    f"a {nuevo_estado}."
                )

            # =================================================
            # RESTAURACIÓN DEL STOCK
            # =================================================
            #
            # Solo restauramos stock cuando:
            #
            # PAGADO -> CANCELADO
            #
            # Esto es importante porque el stock solamente
            # fue descontado cuando la compra pasó a PAGADO.
            #
            # Usamos F() para que el incremento se calcule
            # en PostgreSQL sobre el valor vigente, sin pisar
            # descuentos hechos por compras concurrentes.
            #

            if (
                estado_anterior == Compra.Estado.PAGADO
                and nuevo_estado == Compra.Estado.CANCELADO
            ):

                for item in compra.items.order_by("sector_id"):

                    Sector.objects.filter(
                        pk=item.sector_id
                    ).update(
                        stock=F("stock") + item.cantidad
                    )

            # =================================================
            # ACTUALIZAR ESTADO DE LA COMPRA
            # =================================================

            compra.estado = nuevo_estado

            compra.save(
                update_fields=[
                    "estado",
                    "actualizado_en",
                ]
            )

        # ====================================================
        # RESPUESTA
        # ====================================================

        return Response(
            {
                "mensaje": (
                    "Estado de la compra actualizado."
                ),
                "compra": CompraSerializer(
                    compra
                ).data,
            },
            status=status.HTTP_200_OK,
        )
