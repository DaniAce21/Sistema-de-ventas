"""
Pruebas de autenticación JWT y de la documentación protegida por RBAC.
"""

from django.urls import reverse

from rest_framework.test import APITestCase

from .models import Usuario


class RegistroTest(APITestCase):

    def registrar(self, **extra):
        datos = {
            "username": "nuevo",
            "email": "nuevo@correo.cl",
            "password": "Entradas-2026!",
            **extra,
        }
        return self.client.post(reverse("registro"), datos, format="json")

    def test_registro_crea_espectador_aunque_se_envie_otro_rol(self):
        respuesta = self.registrar(rol="ORGANIZADOR")

        self.assertEqual(respuesta.status_code, 201)
        self.assertNotIn("password", respuesta.data)
        usuario = Usuario.objects.get(username="nuevo")
        self.assertEqual(usuario.rol, Usuario.Rol.ESPECTADOR)
        self.assertTrue(usuario.check_password("Entradas-2026!"))

    def test_contrasena_debil_es_rechazada(self):
        respuesta = self.registrar(password="123")

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("password", respuesta.data["campos"])

    def test_correo_duplicado_es_rechazado(self):
        self.registrar()

        respuesta = self.registrar(username="otro")

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("email", respuesta.data["campos"])

    def test_perfil_del_usuario_autenticado(self):
        self.registrar()
        self.client.login(username="nuevo", password="Entradas-2026!")
        usuario = Usuario.objects.get(username="nuevo")
        self.client.force_authenticate(usuario)

        respuesta = self.client.get(reverse("perfil"))

        self.assertEqual(respuesta.data["rol"], "ESPECTADOR")
        self.assertEqual(respuesta.data["email"], "nuevo@correo.cl")


class DocumentacionRBACTest(APITestCase):

    def setUp(self):
        self.url_docs = reverse("swagger-ui")
        self.url_schema = reverse("schema")

        for username, rol in [
            ("fan", Usuario.Rol.ESPECTADOR),
            ("org", Usuario.Rol.ORGANIZADOR),
        ]:
            Usuario.objects.create_user(
                username=username, password="clave-segura-123", rol=rol,
            )

    def token(self, username):
        respuesta = self.client.post(
            reverse("token-obtain"),
            {"username": username, "password": "clave-segura-123"},
            format="json",
        )
        return respuesta.data["access"]

    def test_anonimo_es_redirigido_al_login(self):
        respuesta = self.client.get(self.url_docs)

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("rest_framework:login"), respuesta["Location"])

    def test_espectador_recibe_403(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token('fan')}")

        self.assertEqual(self.client.get(self.url_docs).status_code, 403)
        self.assertEqual(self.client.get(self.url_schema).status_code, 403)

    def test_organizador_accede_con_jwt(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token('org')}")

        self.assertEqual(self.client.get(self.url_docs).status_code, 200)
        self.assertEqual(self.client.get(self.url_schema).status_code, 200)

    def test_organizador_accede_con_sesion(self):
        self.client.login(username="org", password="clave-segura-123")

        self.assertEqual(self.client.get(self.url_docs).status_code, 200)

    def test_superusuario_accede(self):
        Usuario.objects.create_superuser(
            username="admin", password="clave-segura-123",
        )
        self.client.login(username="admin", password="clave-segura-123")

        self.assertEqual(self.client.get(self.url_schema).status_code, 200)

    def test_jwt_incluye_el_rol(self):
        import jwt

        payload = jwt.decode(self.token("org"), options={"verify_signature": False})

        self.assertEqual(payload["rol"], "ORGANIZADOR")
