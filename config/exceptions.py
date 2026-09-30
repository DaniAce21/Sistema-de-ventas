"""
Manejo centralizado de errores de la API.

DRF devuelve los errores con formatos distintos según su origen:

    {"detail": "No encontrado."}                        (404, 401, 403)
    {"cantidad": ["Asegúrese de que ..."]}              (validación)
    {"error": "Stock insuficiente ..."}                 (nuestras vistas)

Este manejador los unifica en una sola estructura, para que el
frontend siempre lea el mensaje del mismo lugar:

    {
        "error": "Mensaje legible para el usuario.",
        "codigo": 400,
        "campos": {"cantidad": ["..."]}     <- solo en errores de validación
    }

Se registra en settings.REST_FRAMEWORK["EXCEPTION_HANDLER"].
"""

import logging

from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


logger = logging.getLogger(__name__)


def primer_mensaje(data):
    """
    Obtiene el primer mensaje de texto de una estructura de errores
    (diccionario, lista o texto), recorriéndola en profundidad.
    """

    if isinstance(data, dict):
        for valor in data.values():
            return primer_mensaje(valor)
        return ""

    if isinstance(data, list):
        return primer_mensaje(data[0]) if data else ""

    return str(data)


def manejador_errores(exc, context):
    """
    Envuelve el manejador por defecto de DRF.
    """

    response = exception_handler(exc, context)

    # --------------------------------------------------------
    # ERRORES NO CONTROLADOS (500)
    # --------------------------------------------------------
    #
    # DRF devuelve None para excepciones que no conoce.
    # En desarrollo (DEBUG) dejamos que Django muestre la
    # traza completa; en producción respondemos un JSON
    # genérico sin exponer detalles internos.
    #
    if response is None:
        if settings.DEBUG:
            return None

        logger.exception("Error no controlado en la API", exc_info=exc)

        return Response(
            {
                "error": "Ocurrió un error inesperado. Intente nuevamente.",
                "codigo": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = response.data
    cuerpo = {"codigo": response.status_code}

    if isinstance(data, dict) and "error" in data:
        # Error lanzado por nuestras vistas: {"error": "..."}
        cuerpo["error"] = primer_mensaje(data["error"])

    elif isinstance(data, dict) and "detail" in data:
        # Error estándar de DRF: {"detail": "..."}
        cuerpo["error"] = str(data["detail"])

    else:
        # Error de validación por campo: {"campo": ["..."]}
        cuerpo["error"] = primer_mensaje(data)
        cuerpo["campos"] = data

    response.data = cuerpo

    return response
