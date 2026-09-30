"""
Configuración del panel administrativo de Django.

Aquí registramos los modelos de la aplicación eventos
para poder administrarlos desde /admin/.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Recinto, Evento, Sector


# ------------------------------------------------------------
# SECTORES DENTRO DEL EVENTO
# ------------------------------------------------------------
#
# TabularInline permite crear y editar los sectores (precio y
# stock) directamente en la ficha del evento.
class SectorInline(admin.TabularInline):
    model = Sector
    extra = 1
    fields = ("nombre", "precio", "stock")


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    """
    Gestión de eventos con miniatura del afiche, filtros por
    los CHOICES (estado y categoría) y búsqueda por nombre.
    """

    list_display = (
        "miniatura",
        "nombre",
        "categoria",
        "estado",
        "fecha",
        "recinto",
        "organizador",
    )
    list_display_links = ("miniatura", "nombre")
    list_filter = ("estado", "categoria", "recinto")
    search_fields = ("nombre", "descripcion", "recinto__nombre")
    date_hierarchy = "fecha"
    list_select_related = ("recinto", "organizador")
    readonly_fields = ("vista_previa",)
    inlines = [SectorInline]

    fieldsets = (
        ("Información del evento", {
            "fields": ("nombre", "descripcion", "categoria", "estado", "fecha"),
        }),
        ("Lugar y responsable", {
            "fields": ("recinto", "organizador"),
        }),
        ("Afiche", {
            "fields": ("imagen", "vista_previa"),
        }),
    )

    @admin.display(description="Afiche")
    def miniatura(self, obj):
        """
        Imagen pequeña en el listado. format_html escapa los valores
        para evitar inyección de HTML.
        """

        if not obj.imagen:
            return "—"

        return format_html(
            '<img src="{}" class="miniatura-afiche" alt="">',
            obj.imagen.url,
        )

    @admin.display(description="Vista previa")
    def vista_previa(self, obj):
        """
        Imagen grande dentro de la ficha del evento.
        """

        if not obj.imagen:
            return "Sin afiche"

        return format_html(
            '<img src="{}" class="vista-afiche" alt="">',
            obj.imagen.url,
        )


@admin.register(Recinto)
class RecintoAdmin(admin.ModelAdmin):
    """
    Recintos donde se realizan los eventos.
    """

    list_display = ("nombre", "direccion")
    search_fields = ("nombre", "direccion")


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    """
    Listado general de sectores para revisar precios y stock.
    """

    list_display = ("nombre", "evento", "precio", "stock")
    list_filter = ("evento__estado", "evento")
    search_fields = ("nombre", "evento__nombre")
    list_select_related = ("evento",)
    list_editable = ("precio", "stock")
