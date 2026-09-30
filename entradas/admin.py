"""
Configuración del panel administrativo para las entradas.

Permite buscar una entrada por su código UUID, por ejemplo
para validarla en el acceso al evento.
"""

from django.contrib import admin

from .models import Entrada


@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    """
    Listado de entradas con su compra, sector y uso.
    """

    list_display = ("id", "compra", "sector", "utilizada", "creada_en")
    list_filter = ("utilizada", "sector__evento")
    search_fields = ("id", "compra__usuario__username")
    readonly_fields = ("id", "compra", "sector", "creada_en")
