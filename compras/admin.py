"""
Configuración del panel administrativo para las compras.

Permite revisar desde /admin/ el historial de órdenes,
sus estados y las líneas compradas.
"""

from django.contrib import admin

from .models import Compra, ItemCompra


class ItemCompraInline(admin.TabularInline):
    """
    Muestra las líneas históricas dentro de la ficha de la compra.

    Son de solo lectura: el historial no debe modificarse.
    """

    model = ItemCompra
    extra = 0
    readonly_fields = ("sector", "cantidad", "precio_unitario", "subtotal")
    can_delete = False


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    """
    Listado de compras filtrable por estado.

    IMPORTANTE: cambiar el estado desde aquí NO repone stock.
    Para cancelar con reposición se debe usar el endpoint
    PATCH /api/compras/{id}/estado/, que contiene esa lógica.
    """

    list_display = ("id", "usuario", "estado", "total", "creado_en")
    list_filter = ("estado",)
    search_fields = ("usuario__username",)
    readonly_fields = ("usuario", "estado", "total", "creado_en", "actualizado_en")
    inlines = [ItemCompraInline]
