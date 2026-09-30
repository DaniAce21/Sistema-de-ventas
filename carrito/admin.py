"""
Configuración del panel administrativo para el carrito.

Permite ver desde /admin/ el carrito persistente de cada
usuario y sus items, lo que sirve para comprobar que los
items siguen guardados en PostgreSQL tras un logout.
"""

from django.contrib import admin

from .models import Carrito, ItemCarrito


class ItemCarritoInline(admin.TabularInline):
    """
    Muestra los items dentro de la ficha del carrito.
    """

    model = ItemCarrito
    extra = 0


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    """
    Listado de carritos con su usuario y fecha de actualización.
    """

    list_display = ("id", "usuario", "actualizado_en")
    search_fields = ("usuario__username",)
    inlines = [ItemCarritoInline]
