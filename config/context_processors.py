"""
Context processors del proyecto.

Un context processor es una función que Django ejecuta
al renderizar cada plantilla HTML. El diccionario que
devuelve queda disponible como variables en la plantilla.
"""

from django.conf import settings


def alumno(request):
    """
    Expone los datos del alumno (settings.ALUMNO) como
    {{ alumno.nombre }}, {{ alumno.seccion }} y {{ alumno.anio }}.

    Lo usa templates/includes/footer_alumno.html.
    """

    return {
        "alumno": settings.ALUMNO,
    }
