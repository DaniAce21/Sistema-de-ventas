"""
Pruebas del catálogo: filtros django-filter, búsqueda,
gestión de inventario por el organizador y footer del alumno.
"""

from datetime import timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from usuarios.models import Usuario

from .models import Evento, Recinto, Sector


class CatalogoBaseTest(APITestCase):
    """
    Eventos de prueba:

    - "Rock Fest"  (PROGRAMADO, CONCIERTO, en 10 días): sector de $20.000 con stock.
    - "Jazz Night" (PROGRAMADO, TEATRO, en 60 días):    sector de $80.000 agotado.
    - "Suspendido" (CANCELADO, en 20 días):             no visible para el público.
    """

    def setUp(self):
        self.organizador = Usuario.objects.create_user(
            username="org", password="clave-segura-123",
            rol=Usuario.Rol.ORGANIZADOR,
        )
        self.arena = Recinto.objects.create(nombre="Arena", direccion="Calle 1")
        teatro = Recinto.objects.create(nombre="Teatro", direccion="Calle 2")

        self.rock = Evento.objects.create(
            nombre="Rock Fest",
            fecha=timezone.now() + timedelta(days=10),
            recinto=self.arena,
            organizador=self.organizador,
        )
        self.jazz = Evento.objects.create(
            nombre="Jazz Night",
            fecha=timezone.now() + timedelta(days=60),
            categoria=Evento.Categoria.TEATRO,
            recinto=teatro,
            organizador=self.organizador,
        )
        self.suspendido = Evento.objects.create(
            nombre="Suspendido",
            fecha=timezone.now() + timedelta(days=20),
            estado=Evento.Estado.CANCELADO,
            recinto=self.arena,
            organizador=self.organizador,
        )
        self.cancha = Sector.objects.create(
            evento=self.rock, nombre="Cancha", precio=20000, stock=100,
        )
        Sector.objects.create(
            evento=self.jazz, nombre="VIP", precio=80000, stock=0,
        )

        self.url = reverse("eventos-lista-crear")

    def nombres(self, **params):
        respuesta = self.client.get(self.url, params)
        self.assertEqual(respuesta.status_code, 200)
        return {evento["nombre"] for evento in respuesta.data}


class VisibilidadPorRolTest(CatalogoBaseTest):

    def test_publico_solo_ve_eventos_programados(self):
        self.assertEqual(self.nombres(), {"Rock Fest", "Jazz Night"})

        detalle = self.client.get(reverse("evento-detalle", args=[self.suspendido.id]))
        self.assertEqual(detalle.status_code, 404)

    def test_espectador_solo_ve_eventos_programados(self):
        espectador = Usuario.objects.create_user(username="fan", password="clave-segura-123")
        self.client.force_authenticate(espectador)

        self.assertNotIn("Suspendido", self.nombres())

    def test_organizador_ve_todos_sus_eventos(self):
        self.client.force_authenticate(self.organizador)

        self.assertEqual(self.nombres(), {"Rock Fest", "Jazz Night", "Suspendido"})

    def test_organizador_no_ve_eventos_ajenos(self):
        otro = Usuario.objects.create_user(
            username="otro", password="clave-segura-123",
            rol=Usuario.Rol.ORGANIZADOR,
        )
        self.client.force_authenticate(otro)

        self.assertEqual(self.nombres(), set())

    def test_tarjeta_incluye_precio_desde_y_disponibles(self):
        Sector.objects.create(evento=self.rock, nombre="VIP", precio=90000, stock=5)

        respuesta = self.client.get(reverse("evento-detalle", args=[self.rock.id]))

        self.assertEqual(respuesta.data["precio_desde"], "20000.00")
        self.assertEqual(respuesta.data["disponibles"], 105)
        self.assertEqual(respuesta.data["categoria_display"], "Conciertos")


class FiltrosEventosTest(CatalogoBaseTest):

    def test_filtro_por_estado(self):
        self.client.force_authenticate(self.organizador)
        self.assertEqual(self.nombres(estado="CANCELADO"), {"Suspendido"})

    def test_filtro_por_categoria(self):
        self.assertEqual(self.nombres(categoria="TEATRO"), {"Jazz Night"})

    def test_estado_invalido_devuelve_400(self):
        self.assertEqual(self.client.get(self.url, {"estado": "OTRO"}).status_code, 400)

    def test_filtro_por_nombre_parcial(self):
        self.assertEqual(self.nombres(nombre="jazz"), {"Jazz Night"})

    def test_filtro_por_recinto(self):
        # "Suspendido" también está en la Arena, pero no es visible.
        self.assertEqual(self.nombres(recinto=self.arena.id), {"Rock Fest"})

    def test_filtro_por_rango_de_fechas(self):
        hasta = (timezone.localdate() + timedelta(days=30)).isoformat()
        self.assertEqual(self.nombres(fecha_hasta=hasta), {"Rock Fest"})

    def test_filtro_por_rango_de_precios(self):
        self.assertEqual(self.nombres(precio_max=30000), {"Rock Fest"})
        self.assertEqual(self.nombres(precio_min=50000), {"Jazz Night"})

    def test_filtro_con_stock(self):
        self.assertEqual(self.nombres(con_stock="true"), {"Rock Fest"})
        self.assertEqual(self.nombres(con_stock="false"), {"Jazz Night"})

    def test_estado_invalido_con_formato_de_error_unificado(self):
        respuesta = self.client.get(self.url, {"categoria": "OTRA"})

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.data["codigo"], 400)
        self.assertIn("categoria", respuesta.data["campos"])
        self.assertTrue(respuesta.data["error"])

    def test_busqueda_por_recinto(self):
        self.assertEqual(self.nombres(search="teatro"), {"Jazz Night"})

    def test_orden_descendente_por_fecha(self):
        respuesta = self.client.get(self.url, {"ordering": "-fecha"})
        self.assertEqual(respuesta.data[0]["nombre"], "Jazz Night")

    def test_filtros_de_sectores(self):
        Sector.objects.create(evento=self.rock, nombre="VIP", precio=90000, stock=0)
        url = reverse("evento-sectores", args=[self.rock.id])

        disponibles = self.client.get(url, {"disponible": "true"}).data
        self.assertEqual([s["nombre"] for s in disponibles], ["Cancha"])

        caros = self.client.get(url, {"precio_min": 50000}).data
        self.assertEqual([s["nombre"] for s in caros], ["VIP"])


class InventarioTest(CatalogoBaseTest):

    def test_organizador_crea_sector_y_ajusta_stock(self):
        self.client.force_authenticate(self.organizador)

        creado = self.client.post(
            reverse("evento-sectores", args=[self.rock.id]),
            {"nombre": "Platea", "precio": "35000.00", "stock": 50},
            format="json",
        )
        self.assertEqual(creado.status_code, 201)

        editado = self.client.patch(
            reverse("sector-detalle", args=[creado.data["id"]]),
            {"stock": 80},
            format="json",
        )
        self.assertEqual(editado.status_code, 200)
        self.assertEqual(Sector.objects.get(pk=creado.data["id"]).stock, 80)

    def test_organizador_ajeno_no_modifica_inventario(self):
        otro = Usuario.objects.create_user(
            username="otro", password="clave-segura-123",
            rol=Usuario.Rol.ORGANIZADOR,
        )
        self.client.force_authenticate(otro)

        respuesta = self.client.patch(
            reverse("sector-detalle", args=[self.cancha.id]),
            {"stock": 0},
            format="json",
        )

        self.assertEqual(respuesta.status_code, 404)
        self.cancha.refresh_from_db()
        self.assertEqual(self.cancha.stock, 100)

    def test_espectador_no_modifica_inventario(self):
        espectador = Usuario.objects.create_user(
            username="fan", password="clave-segura-123",
        )
        self.client.force_authenticate(espectador)

        respuesta = self.client.patch(
            reverse("sector-detalle", args=[self.cancha.id]),
            {"stock": 0},
            format="json",
        )

        self.assertEqual(respuesta.status_code, 403)

    def test_organizador_crea_evento_con_recinto(self):
        self.client.force_authenticate(self.organizador)

        respuesta = self.client.post(
            self.url,
            {
                "nombre": "Nuevo",
                "fecha": (timezone.now() + timedelta(days=5)).isoformat(),
                "recinto_id": self.arena.id,
            },
            format="json",
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data["recinto"]["nombre"], "Arena")


class RecintosTest(CatalogoBaseTest):

    def test_listado_publico_y_creacion_solo_organizador(self):
        url = reverse("recintos")

        self.assertEqual(len(self.client.get(url).data), 2)
        self.assertEqual(
            self.client.post(url, {"nombre": "X", "direccion": "Y"}).status_code,
            401,
        )

        self.client.force_authenticate(self.organizador)
        self.assertEqual(
            self.client.post(url, {"nombre": "Estadio", "direccion": "Av. 1"}).status_code,
            201,
        )


class PaginasHTMLTest(APITestCase):

    def test_portada_del_backend(self):
        respuesta = self.client.get("/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, settings.ALUMNO["nombre"])

    def test_pagina_404_personalizada(self):
        with self.settings(DEBUG=False):
            respuesta = self.client.get("/no-existe/")

        self.assertEqual(respuesta.status_code, 404)
        self.assertContains(respuesta, "Página no encontrada", status_code=404)
        self.assertContains(respuesta, settings.ALUMNO["nombre"], status_code=404)


class FooterAlumnoTest(APITestCase):

    def test_endpoint_publico_con_datos_del_alumno(self):
        respuesta = self.client.get(reverse("alumno"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data, settings.ALUMNO)

    def test_footer_en_login_y_swagger(self):
        nombre = settings.ALUMNO["nombre"]

        login = self.client.get(reverse("rest_framework:login"))
        self.assertContains(login, nombre)

        Usuario.objects.create_user(
            username="org", password="clave-segura-123",
            rol=Usuario.Rol.ORGANIZADOR,
        )
        self.client.login(username="org", password="clave-segura-123")
        self.assertContains(self.client.get(reverse("swagger-ui")), nombre)

    def test_footer_en_admin(self):
        Usuario.objects.create_superuser(username="admin", password="clave-segura-123")
        self.client.login(username="admin", password="clave-segura-123")

        self.assertContains(self.client.get("/admin/"), settings.ALUMNO["nombre"])
