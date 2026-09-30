"""
Vistas de la aplicación eventos.

Aquí definimos los endpoints relacionados con:

- Consulta pública de eventos (con filtros, búsqueda y orden).
- Consulta pública de sectores.
- Creación, modificación y eliminación de eventos.
- Gestión de inventario: creación de sectores y ajuste de stock.
- Recintos disponibles para crear eventos.

Visibilidad según el rol (RBAC):

    Visitante / ESPECTADOR:
        Solo eventos PROGRAMADOS (los que se pueden comprar).

    ORGANIZADOR (administrador):
        Todos SUS eventos en cualquier estado, y es el único
        que puede crearlos, modificarlos o eliminarlos.
"""

from django.db.models import Min, ProtectedError, Sum
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from .filters import EventoFilter, SectorFilter
from .models import Evento, Recinto, Sector
from .serializers import EventoSerializer, RecintoSerializer, SectorSerializer
from usuarios.models import Usuario
from usuarios.permissions import IsOrganizador


def es_organizador(user):
    """
    True si el usuario autenticado tiene rol ORGANIZADOR.
    """

    return (
        user.is_authenticated
        and user.rol == Usuario.Rol.ORGANIZADOR
    )


def eventos_visibles(user):
    """
    QuerySet base de eventos según quién consulta.

    - ORGANIZADOR: sus propios eventos, en cualquier estado.
    - Resto: solo eventos PROGRAMADOS de cualquier organizador.

    Además anotamos en la misma consulta SQL el precio mínimo
    y el stock total de los sectores (para las tarjetas del
    catálogo), evitando una consulta extra por cada evento.
    """

    queryset = (
        Evento.objects
        .select_related("recinto", "organizador")
        .annotate(
            precio_desde=Min("sectores__precio"),
            disponibles=Sum("sectores__stock"),
        )
    )

    if es_organizador(user):
        return queryset.filter(organizador=user)

    return queryset.filter(estado=Evento.Estado.PROGRAMADO)


class LecturaPublicaMixin:
    """
    Permisos compartidos por las vistas del catálogo.

    GET (lectura):
        Cualquier persona, incluso sin iniciar sesión.

    POST / PUT / PATCH / DELETE (gestión):
        Solamente usuarios con rol ORGANIZADOR.
    """

    def get_permissions(self):
        """
        Determina qué permiso se utiliza dependiendo
        del método HTTP solicitado.
        """

        if self.request.method == "GET":
            return [AllowAny()]

        return [
            IsAuthenticated(),
            IsOrganizador(),
        ]


def eliminar_protegido(instancia, mensaje):
    """
    Elimina un registro controlando la integridad referencial.

    ItemCompra y Entrada apuntan a Sector con on_delete=PROTECT:
    PostgreSQL no permite borrar sectores (ni eventos) que ya
    tienen entradas vendidas. En lugar de un error 500,
    respondemos 400 con un mensaje claro.
    """

    try:
        instancia.delete()
    except ProtectedError:
        raise ValidationError({"error": mensaje})


class EventoListCreateView(LecturaPublicaMixin, generics.ListCreateAPIView):
    """
    Lista los eventos y permite crear nuevos eventos.

        GET  /api/eventos/   Público (solo PROGRAMADOS) u ORGANIZADOR (los suyos).
        POST /api/eventos/   ORGANIZADOR. Acepta multipart para subir el afiche.

    Filtros disponibles (ver eventos/filters.py):

        ?nombre=rock
        ?categoria=CONCIERTO
        ?estado=PROGRAMADO
        ?recinto=1
        ?fecha_desde=2026-10-01&fecha_hasta=2026-12-31
        ?precio_min=10000&precio_max=50000
        ?con_stock=true

    Búsqueda y orden:

        ?search=arena          (nombre, descripción o recinto)
        ?ordering=-fecha       (fecha o nombre; "-" = descendente)
    """

    serializer_class = EventoSerializer

    def get_queryset(self):
        """
        Eventos visibles para el usuario, ordenados por fecha.
        """

        return eventos_visibles(self.request.user).order_by("fecha")

    # --------------------------------------------------------
    # FILTROS, BÚSQUEDA Y ORDEN
    # --------------------------------------------------------
    #
    # Los backends se configuran globalmente en settings.py.
    # Aquí indicamos sobre qué campos operan en esta vista.
    #
    filterset_class = EventoFilter

    search_fields = [
        "nombre",
        "descripcion",
        "recinto__nombre",
    ]

    ordering_fields = [
        "fecha",
        "nombre",
    ]

    def perform_create(self, serializer):
        """
        Guarda el evento asociándolo automáticamente
        al organizador que realizó la petición.

        De esta forma el frontend no necesita enviar
        manualmente el ID del organizador.
        """

        serializer.save(
            organizador=self.request.user
        )


class EventoDetailView(LecturaPublicaMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Permite consultar, modificar y eliminar un evento.

        GET              /api/eventos/{id}/   Público (solo PROGRAMADOS).
        PUT/PATCH/DELETE /api/eventos/{id}/   ORGANIZADOR propietario.
    """

    serializer_class = EventoSerializer

    def get_queryset(self):
        """
        Reutiliza la misma regla de visibilidad del listado:

        - Visitante/ESPECTADOR: un evento no PROGRAMADO responde 404.
        - ORGANIZADOR: solo sus propios eventos; uno ajeno responde 404,
          por lo que tampoco puede modificarlo ni eliminarlo.
        """

        return eventos_visibles(self.request.user)

    def perform_destroy(self, instance):
        eliminar_protegido(
            instance,
            "No se puede eliminar un evento con entradas vendidas. "
            "Cámbielo a estado CANCELADO.",
        )


class SectorListCreateView(LecturaPublicaMixin, generics.ListCreateAPIView):
    """
    Lista y crea los sectores de un evento.

        GET  /api/eventos/{id}/sectores/   Público.
        POST /api/eventos/{id}/sectores/   ORGANIZADOR propietario.

    Filtros disponibles (ver eventos/filters.py):

        ?precio_min=10000&precio_max=50000
        ?disponible=true
        ?ordering=precio
    """

    serializer_class = SectorSerializer

    filterset_class = SectorFilter

    ordering_fields = [
        "precio",
        "stock",
        "nombre",
    ]

    def get_queryset(self):
        """
        Obtiene solamente los sectores del evento
        indicado en la URL.
        """

        # drf-spectacular inspecciona la vista sin kwargs reales.
        if getattr(self, "swagger_fake_view", False):
            return Sector.objects.none()

        evento_id = self.kwargs["pk"]

        # Mismas reglas de visibilidad que el evento: un visitante
        # no puede ver sectores de eventos cancelados o finalizados.
        visibles = eventos_visibles(self.request.user).values("id")

        return Sector.objects.filter(
            evento_id=evento_id,
            evento_id__in=visibles,
        ).order_by("precio")

    def perform_create(self, serializer):
        """
        Crea un sector dentro del evento de la URL.

        Solo el organizador dueño del evento puede agregarle
        sectores; si el evento es de otro organizador, 404.
        """

        evento = get_object_or_404(
            Evento,
            pk=self.kwargs["pk"],
            organizador=self.request.user,
        )

        serializer.save(evento=evento)


class SectorDetailView(LecturaPublicaMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Gestión de inventario de un sector.

        GET              /api/eventos/sectores/{id}/   Público.
        PUT/PATCH/DELETE /api/eventos/sectores/{id}/   ORGANIZADOR propietario.

    Ejemplo, reponer stock manualmente:

        PATCH /api/eventos/sectores/3/   {"stock": 200}
    """

    serializer_class = SectorSerializer

    def get_queryset(self):
        """
        GET: cualquier sector.
        Modificación: solo sectores de eventos del organizador.
        """

        queryset = Sector.objects.select_related("evento")

        if self.request.method == "GET":
            return queryset

        return queryset.filter(
            evento__organizador=self.request.user
        )

    def perform_destroy(self, instance):
        eliminar_protegido(
            instance,
            "No se puede eliminar un sector con entradas vendidas.",
        )


class RecintoListCreateView(LecturaPublicaMixin, generics.ListCreateAPIView):
    """
    Recintos donde se realizan los eventos.

        GET  /api/eventos/recintos/   Público.
        POST /api/eventos/recintos/   ORGANIZADOR.

    El administrador los usa al crear un evento.
    """

    queryset = Recinto.objects.order_by("nombre")
    serializer_class = RecintoSerializer

    search_fields = ["nombre", "direccion"]
