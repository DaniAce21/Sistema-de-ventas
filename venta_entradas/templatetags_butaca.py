"""
Etiquetas de plantilla propias del proyecto.

Se registran como "builtins" en settings.TEMPLATES, por lo que
están disponibles en TODAS las plantillas sin usar {% load %}.

    {% footer_alumno %}   Footer con nombre, sección y año.

Por qué una etiqueta y no solo el context processor:
la página de error 500 se renderiza SIN contexto de request
(Django no ejecuta context processors ahí, porque el error
podría venir justamente de uno de ellos). Una inclusion tag
lee settings.ALUMNO directamente y funciona en cualquier página.
"""

from django import template
from django.conf import settings


register = template.Library()


@register.inclusion_tag("includes/footer_alumno.html")
def footer_alumno():
    """
    Renderiza templates/includes/footer_alumno.html
    con los datos de settings.ALUMNO.
    """

    return {
        "alumno": settings.ALUMNO,
    }
