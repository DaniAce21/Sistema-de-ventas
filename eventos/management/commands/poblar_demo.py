"""
Comando de gestión: carga datos de demostración.

    python manage.py poblar_demo

Crea (solo si no existen, se puede ejecutar varias veces):

- Un administrador:  admin_demo  / Butaca-2026   (rol ORGANIZADOR)
- Un espectador:     fan_demo    / Butaca-2026   (rol ESPECTADOR)
- Recintos, eventos de todas las categorías y sus sectores.

Los eventos quedan a nombre de admin_demo. Los afiches se pueden
subir después desde el panel web o desde /admin/.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from eventos.models import Evento, Recinto, Sector
from usuarios.models import Usuario


CLAVE_DEMO = "Butaca-2026"

RECINTOS = [
    ("Movistar Arena", "Av. Beaucheff 1204, Santiago"),
    ("Teatro Municipal de Temuco", "Av. Pablo Neruda 01520, Temuco"),
    ("Estadio Germán Becker", "Av. Pablo Neruda 1420, Temuco"),
    ("Parque O'Higgins", "Av. Tupper 1400, Santiago"),
]

# (nombre, categoría, recinto, días desde hoy, hora, descripción, [(sector, precio, stock)])
EVENTOS = [
    (
        "Noche de Rock Sureño", "CONCIERTO", 0, 12, 21,
        "Las mejores bandas del sur de Chile en una sola noche de guitarras y energía.",
        [("Cancha", 25000, 800), ("Platea", 38000, 300), ("VIP", 65000, 60)],
    ),
    (
        "Festival Araucanía Sonora", "FESTIVAL", 3, 25, 14,
        "Dos escenarios, doce artistas y lo mejor de la música independiente al aire libre.",
        [("General", 32000, 2500), ("Preferencial", 55000, 500)],
    ),
    (
        "La Casa de Bernarda Alba", "TEATRO", 1, 8, 20,
        "Montaje clásico de García Lorca con elenco regional.",
        [("Platea baja", 18000, 120), ("Platea alta", 12000, 180), ("Palco", 28000, 8)],
    ),
    (
        "Stand-up: Humor en Serio", "STANDUP", 1, 5, 21,
        "Una hora y media de comedia observacional sin filtro.",
        [("General", 15000, 250)],
    ),
    (
        "Clásico del Sur", "DEPORTE", 2, 18, 18,
        "El partido más esperado de la temporada en el Germán Becker.",
        [("Galería", 8000, 3000), ("Tribuna", 16000, 1200), ("Palco", 40000, 40)],
    ),
    (
        "Circo de las Burbujas", "FAMILIAR", 1, 15, 16,
        "Espectáculo familiar con acróbatas, música y burbujas gigantes.",
        [("Adulto", 10000, 200), ("Niño", 6000, 200)],
    ),
    (
        "Sinfonía Bajo las Estrellas", "CONCIERTO", 3, 40, 20,
        "Orquesta sinfónica interpretando bandas sonoras del cine.",
        [("General", 20000, 1500), ("Butaca numerada", 35000, 400)],
    ),
    (
        "Electro Pulse", "FESTIVAL", 0, 55, 22,
        "Festival de música electrónica con DJs nacionales e internacionales.",
        [("Early bird", 28000, 0), ("General", 36000, 1800), ("Backstage", 90000, 30)],
    ),
]


class Command(BaseCommand):
    help = "Carga usuarios, recintos, eventos y sectores de demostración."

    @transaction.atomic
    def handle(self, *args, **options):
        admin = self.usuario("admin_demo", Usuario.Rol.ORGANIZADOR, "Administrador", "Demo")
        self.usuario("fan_demo", Usuario.Rol.ESPECTADOR, "Fan", "Demo")

        recintos = [
            Recinto.objects.get_or_create(nombre=nombre, defaults={"direccion": direccion})[0]
            for nombre, direccion in RECINTOS
        ]

        creados = 0
        hoy = timezone.localtime().replace(minute=0, second=0, microsecond=0)

        for nombre, cat, recinto, dias, hora, descripcion, sectores in EVENTOS:
            evento, nuevo = Evento.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "categoria": cat,
                    "recinto": recintos[recinto],
                    "fecha": (hoy + timedelta(days=dias)).replace(hour=hora),
                    "descripcion": descripcion,
                    "organizador": admin,
                },
            )

            if nuevo:
                creados += 1
                Sector.objects.bulk_create(
                    Sector(evento=evento, nombre=s, precio=p, stock=st)
                    for s, p, st in sectores
                )

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {creados} eventos nuevos. "
            f"Usuarios: admin_demo / fan_demo (clave {CLAVE_DEMO})."
        ))

    def usuario(self, username, rol, nombre, apellido):
        """
        Crea el usuario si no existe (create_user guarda la clave con hash).
        """

        usuario = Usuario.objects.filter(username=username).first()

        if usuario is None:
            usuario = Usuario.objects.create_user(
                username=username,
                password=CLAVE_DEMO,
                email=f"{username}@butaca.cl",
                first_name=nombre,
                last_name=apellido,
                rol=rol,
            )

        return usuario
