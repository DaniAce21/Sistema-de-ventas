"""
Pruebas del flujo completo de compra:

carrito -> checkout -> entradas UUID -> cancelación con reposición de stock.
"""

import uuid
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from entradas.models import Entrada
from eventos.models import Evento, Recinto, Sector
from usuarios.models import Usuario

from .models import Compra


class BaseFlujoTest(APITestCase):
    """
    Crea un organizador, un espectador, un evento y dos sectores.
    """

    def setUp(self):
        self.organizador = Usuario.objects.create_user(
            username="org", password="clave-segura-123",
            rol=Usuario.Rol.ORGANIZADOR,
        )
        self.espectador = Usuario.objects.create_user(
            username="fan", password="clave-segura-123",
            rol=Usuario.Rol.ESPECTADOR,
        )

        recinto = Recinto.objects.create(nombre="Arena", direccion="Calle 1")
        self.evento = Evento.objects.create(
            nombre="Concierto",
            fecha=timezone.now() + timedelta(days=30),
            recinto=recinto,
            organizador=self.organizador,
        )
        self.vip = Sector.objects.create(
            evento=self.evento, nombre="VIP", precio=50000, stock=10,
        )
        self.cancha = Sector.objects.create(
            evento=self.evento, nombre="Cancha", precio=20000, stock=5,
        )

        self.url_carro = reverse("carrito")
        self.url_pagar = reverse("compras-pagar")

    def agregar(self, sector, cantidad):
        return self.client.post(
            self.url_carro,
            {"sector_id": sector.id, "cantidad": cantidad},
            format="json",
        )

    def url_estado(self, compra_id):
        return reverse("compra-cambiar-estado", args=[compra_id])


class CarritoTest(BaseFlujoTest):

    def test_agregar_no_descuenta_stock_y_suma_cantidades(self):
        self.client.force_authenticate(self.espectador)

        self.assertEqual(self.agregar(self.vip, 2).status_code, 201)
        respuesta = self.agregar(self.vip, 3)

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(len(respuesta.data["items"]), 1)
        self.assertEqual(respuesta.data["items"][0]["cantidad"], 5)

        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 10)

    def test_carrito_persiste_entre_peticiones(self):
        self.client.force_authenticate(self.espectador)
        self.agregar(self.vip, 1)

        self.client.force_authenticate(None)
        self.client.force_authenticate(self.espectador)
        respuesta = self.client.get(self.url_carro)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["items"][0]["sector"]["id"], self.vip.id)

    def test_delete_quita_un_sector_o_vacia_el_carrito(self):
        self.client.force_authenticate(self.espectador)
        self.agregar(self.vip, 1)
        self.agregar(self.cancha, 1)

        respuesta = self.client.delete(
            self.url_carro, {"sector_id": self.vip.id}, format="json",
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.data["items"]), 1)

        respuesta = self.client.delete(self.url_carro, {}, format="json")
        self.assertEqual(respuesta.data["items"], [])

    def test_no_se_agregan_sectores_de_eventos_cancelados(self):
        self.evento.estado = Evento.Estado.CANCELADO
        self.evento.save()
        self.client.force_authenticate(self.espectador)

        self.assertEqual(self.agregar(self.vip, 1).status_code, 400)

    def test_organizador_y_anonimo_no_usan_el_carrito(self):
        self.assertEqual(self.client.get(self.url_carro).status_code, 401)

        self.client.force_authenticate(self.organizador)
        self.assertEqual(self.client.get(self.url_carro).status_code, 403)


class CheckoutTest(BaseFlujoTest):

    def test_pago_exitoso_descuenta_stock_y_genera_entradas_uuid(self):
        self.client.force_authenticate(self.espectador)
        self.agregar(self.vip, 2)
        self.agregar(self.cancha, 3)

        respuesta = self.client.post(self.url_pagar, {}, format="json")

        self.assertEqual(respuesta.status_code, 201)
        compra = Compra.objects.get(pk=respuesta.data["compra"]["id"])
        self.assertEqual(compra.estado, Compra.Estado.PAGADO)
        self.assertEqual(compra.total, 2 * 50000 + 3 * 20000)

        self.vip.refresh_from_db()
        self.cancha.refresh_from_db()
        self.assertEqual(self.vip.stock, 8)
        self.assertEqual(self.cancha.stock, 2)

        entradas = Entrada.objects.filter(compra=compra)
        self.assertEqual(entradas.count(), 5)
        ids = {e.id for e in entradas}
        self.assertEqual(len(ids), 5)
        self.assertTrue(all(isinstance(i, uuid.UUID) and i.version == 4 for i in ids))
        self.assertEqual(set(respuesta.data["entradas"]), {str(i) for i in ids})

        # El carrito queda vacío.
        self.assertEqual(self.client.get(self.url_carro).data["items"], [])

        # Las entradas aparecen en /api/mis-entradas/.
        mis_entradas = self.client.get(reverse("mis-entradas"))
        self.assertEqual(len(mis_entradas.data), 5)

    def test_stock_insuficiente_no_modifica_nada(self):
        self.client.force_authenticate(self.espectador)
        self.agregar(self.vip, 1)
        self.agregar(self.cancha, 6)

        respuesta = self.client.post(self.url_pagar, {}, format="json")

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("Stock insuficiente", respuesta.data["error"])
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 10)
        self.assertFalse(Compra.objects.exists())
        self.assertFalse(Entrada.objects.exists())
        self.assertEqual(len(self.client.get(self.url_carro).data["items"]), 2)

    def test_carrito_vacio(self):
        self.client.force_authenticate(self.espectador)

        respuesta = self.client.post(self.url_pagar, {}, format="json")

        self.assertEqual(respuesta.status_code, 400)

    def test_organizador_no_puede_comprar(self):
        self.client.force_authenticate(self.organizador)

        respuesta = self.client.post(self.url_pagar, {}, format="json")

        self.assertEqual(respuesta.status_code, 403)


class CambiarEstadoTest(BaseFlujoTest):

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(self.espectador)
        self.agregar(self.vip, 4)
        respuesta = self.client.post(self.url_pagar, {}, format="json")
        self.compra_id = respuesta.data["compra"]["id"]

    def cambiar(self, estado):
        return self.client.patch(
            self.url_estado(self.compra_id), {"estado": estado}, format="json",
        )

    def test_cancelar_compra_pagada_repone_stock(self):
        self.client.force_authenticate(self.organizador)

        respuesta = self.cambiar(Compra.Estado.CANCELADO)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["compra"]["estado"], "CANCELADO")
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 10)

        # Las entradas de una compra cancelada dejan de mostrarse.
        self.client.force_authenticate(self.espectador)
        self.assertEqual(len(self.client.get(reverse("mis-entradas")).data), 0)

    def test_no_se_puede_reactivar_una_compra_cancelada(self):
        self.client.force_authenticate(self.organizador)
        self.cambiar(Compra.Estado.CANCELADO)

        respuesta = self.cambiar(Compra.Estado.PAGADO)

        self.assertEqual(respuesta.status_code, 400)
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 10)

    def test_entregar_no_modifica_stock(self):
        self.client.force_authenticate(self.organizador)

        self.assertEqual(self.cambiar(Compra.Estado.ENTREGADO).status_code, 200)
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 6)

    def test_espectador_no_puede_cambiar_estado(self):
        self.assertEqual(self.cambiar(Compra.Estado.CANCELADO).status_code, 403)

    def test_listado_de_compras_segun_rol(self):
        url = reverse("compras-lista")
        otro = Usuario.objects.create_user(
            username="otro-org", password="clave-segura-123",
            rol=Usuario.Rol.ORGANIZADOR,
        )

        self.assertEqual(len(self.client.get(url).data), 1)

        self.client.force_authenticate(self.organizador)
        respuesta = self.client.get(url)
        self.assertEqual(len(respuesta.data), 1)
        self.assertEqual(respuesta.data[0]["usuario"], "fan")

        self.client.force_authenticate(otro)
        self.assertEqual(len(self.client.get(url).data), 0)

    def test_resumen_del_dashboard(self):
        url = reverse("compras-resumen")

        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_authenticate(self.organizador)
        resumen = self.client.get(url).data

        self.assertEqual(resumen["entradas_vendidas"], 4)
        self.assertEqual(resumen["recaudado"], "200000.00")
        self.assertEqual(resumen["compras_por_estado"]["PAGADO"], 1)
        evento = resumen["eventos"][0]
        self.assertEqual(evento["vendidas"], 4)
        self.assertEqual(evento["disponibles"], 6 + 5)

        # Una compra cancelada deja de contar como venta.
        self.cambiar(Compra.Estado.CANCELADO)
        resumen = self.client.get(url).data
        self.assertEqual(resumen["entradas_vendidas"], 0)
        self.assertEqual(resumen["compras_por_estado"]["CANCELADO"], 1)

    def test_organizador_ajeno_no_ve_la_compra(self):
        otro = Usuario.objects.create_user(
            username="otro-org", password="clave-segura-123",
            rol=Usuario.Rol.ORGANIZADOR,
        )
        self.client.force_authenticate(otro)

        self.assertEqual(self.cambiar(Compra.Estado.CANCELADO).status_code, 404)
        self.vip.refresh_from_db()
        self.assertEqual(self.vip.stock, 6)
