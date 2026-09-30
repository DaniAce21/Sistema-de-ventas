"""
Configuración principal del proyecto Django.

Proyecto:
Sistema de Venta de Entradas para Eventos y Conciertos

Backend:
Django + Django REST Framework + PostgreSQL

La configuración sensible, como la contraseña de PostgreSQL
y la SECRET_KEY, se obtiene desde el archivo .env.
"""

from pathlib import Path
from datetime import timedelta
import os

from dotenv import load_dotenv


# ============================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================

# BASE_DIR representa la carpeta raíz del proyecto.
# Nos permite construir rutas independientemente del sistema operativo.
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# VARIABLES DE ENTORNO
# ============================================================

# Cargamos las variables almacenadas en el archivo .env.
#
# Esto permite mantener fuera del código fuente información
# sensible como:
# - contraseña de PostgreSQL
# - SECRET_KEY
# - configuración de desarrollo
load_dotenv(BASE_DIR / ".env")


# ============================================================
# SEGURIDAD Y MODO DE DESARROLLO
# ============================================================

# La SECRET_KEY se obtiene desde .env.
# No dejamos la clave directamente escrita en el código.
SECRET_KEY = os.getenv("SECRET_KEY")

# DEBUG controla si Django funciona en modo desarrollo.
# El valor se transforma desde texto ("True"/"False") a booleano.
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Durante el desarrollo permitimos las solicitudes locales.
ALLOWED_HOSTS = []


# ============================================================
# APLICACIONES INSTALADAS
# ============================================================

INSTALLED_APPS = [

    # --------------------------------------------------------
    # Aplicaciones nativas de Django
    # --------------------------------------------------------
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # --------------------------------------------------------
    # Librerías externas
    # --------------------------------------------------------

    # Django REST Framework:
    # permite construir nuestra API REST.
    "rest_framework",

    # django-filter:
    # permite implementar filtros y búsquedas sobre los endpoints.
    "django_filters",

    # drf-spectacular:
    # genera automáticamente la documentación OpenAPI/Swagger.
    "drf_spectacular",

    # --------------------------------------------------------
    # Aplicaciones propias del proyecto
    # --------------------------------------------------------

    "usuarios",
    "eventos",
    "carrito",
    "compras",
    "entradas",
]


# ============================================================
# DATOS DEL ALUMNO (FOOTER)
# ============================================================

# Único lugar donde se definen los datos del alumno.
#
# Se muestran en el footer de:
# - Swagger (/api/docs/), login de la API y panel /admin/
#   mediante el context processor config.context_processors.alumno.
# - El frontend React, que los obtiene desde GET /api/alumno/.
ALUMNO = {
    "nombre": "Daniel Alejandro Aceitón Sepúlveda",
    "seccion": "2026/P TI3041/IEC-N4-C1/D Temuco IEC",
    "anio": 2026,
}


# ============================================================
# USUARIO PERSONALIZADO
# ============================================================

# Indicamos a Django que utilizaremos nuestro modelo Usuario
# ubicado dentro de la aplicación usuarios.
#
# Esto es necesario porque nuestro usuario tendrá un campo
# adicional llamado "rol".
AUTH_USER_MODEL = "usuarios.Usuario"

# Tras iniciar sesión en /api-auth/login/ sin parámetro "next",
# el administrador llega directo a la documentación.
LOGIN_REDIRECT_URL = "/api/docs/"

# Tras cerrar sesión desde Swagger se vuelve a la portada.
LOGOUT_REDIRECT_URL = "/"


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# CONFIGURACIÓN PRINCIPAL DEL PROYECTO
# ============================================================

ROOT_URLCONF = "config.urls"


# ============================================================
# CONFIGURACIÓN DE TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Indicamos que Django también buscará templates
        # dentro de la carpeta /templates ubicada en la raíz.
        "DIRS": [BASE_DIR / "templates"],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # Agrega la variable {{ alumno }} a todas las
                # plantillas HTML que se renderizan con request.
                "config.context_processors.alumno",
            ],

            # Etiquetas disponibles en todas las plantillas sin
            # {% load %}: {% footer_alumno %}.
            "builtins": [
                "config.templatetags_butaca",
            ],
        },
    },
]


# ============================================================
# SERVIDORES WSGI / ASGI
# ============================================================

WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# BASE DE DATOS
# ============================================================

# La pauta exige utilizar PostgreSQL y NO SQLite.
#
# Django se conecta a PostgreSQL mediante psycopg.
#
# Los datos de conexión se obtienen desde el archivo .env.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}


# ============================================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================================

# Estas validaciones son proporcionadas por Django para
# evitar contraseñas demasiado simples o inseguras.
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNACIONALIZACIÓN
# ============================================================

LANGUAGE_CODE = "es"

TIME_ZONE = "America/Santiago"

USE_I18N = True

USE_TZ = True


# ============================================================
# ARCHIVOS ESTÁTICOS
# ============================================================

STATIC_URL = "static/"

# Carpeta con los estilos, logo e íconos propios usados por las
# plantillas HTML (portada, errores, login, Swagger y /admin/).
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# ============================================================
# ARCHIVOS SUBIDOS (MEDIA)
# ============================================================

# Afiches de los eventos subidos por el administrador.
#
# MEDIA_ROOT: carpeta física donde se guardan los archivos.
# MEDIA_URL:  prefijo de la URL pública para acceder a ellos.
#
# En desarrollo Django los sirve desde config/urls.py.
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# CONFIGURACIÓN DE CLAVES PRIMARIAS
# ============================================================

# Django utilizará BigAutoField como tipo de clave primaria
# por defecto para los modelos que no definan una explícitamente.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

# Configuración global de nuestra API REST.
REST_FRAMEWORK = {

    # --------------------------------------------------------
    # Autenticación
    # --------------------------------------------------------
    # Todas las solicitudes protegidas utilizarán JWT.
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    # --------------------------------------------------------
    # Permisos
    # --------------------------------------------------------
    # Por defecto exigimos autenticación.
    #
    # Posteriormente algunos endpoints públicos,
    # como el catálogo de eventos, sobrescribirán
    # este comportamiento utilizando AllowAny.
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),

    # --------------------------------------------------------
    # Filtros
    # --------------------------------------------------------
    # Backends aplicados a todos los endpoints de consulta:
    #
    # - DjangoFilterBackend: filtros por campo definidos en
    #   cada filters.py (?estado=PAGADO, ?precio_max=30000).
    # - SearchFilter: búsqueda de texto libre (?search=rock)
    #   sobre los campos listados en search_fields de la vista.
    # - OrderingFilter: orden de resultados (?ordering=-fecha)
    #   sobre los campos listados en ordering_fields.
    #
    # Cada backend solo actúa si la vista define su
    # configuración (filterset_class, search_fields, etc.).
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),

    # --------------------------------------------------------
    # Documentación OpenAPI
    # --------------------------------------------------------
    # drf-spectacular generará automáticamente
    # el esquema de nuestra API.
    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),

    # --------------------------------------------------------
    # Errores
    # --------------------------------------------------------
    # Todas las respuestas de error de la API tienen el formato
    # {"error": "...", "codigo": 400, "campos": {...}}.
    # Ver config/exceptions.py.
    "EXCEPTION_HANDLER": "config.exceptions.manejador_errores",
}


# ============================================================
# CONFIGURACIÓN JWT
# ============================================================

# SimpleJWT permite trabajar con:
#
# Access Token:
#   se utiliza para acceder a los endpoints protegidos.
#
# Refresh Token:
#   permite obtener un nuevo Access Token cuando este expira.
#
# Más adelante personalizaremos el serializer para incluir
# el rol del usuario dentro del payload JWT.
SIMPLE_JWT = {

    # Tiempo de duración del Access Token.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),

    # Tiempo de duración del Refresh Token.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),

    # Cada vez que se utilice un Refresh Token,
    # se generará uno nuevo.
    "ROTATE_REFRESH_TOKENS": True,

    # Los Refresh Tokens antiguos quedarán invalidados.
    "BLACKLIST_AFTER_ROTATION": True,

    # Las solicitudes autenticadas utilizarán:
    # Authorization: Bearer <token>
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ============================================================
# DOCUMENTACIÓN OPENAPI / SWAGGER
# ============================================================

# Configuración general que aparecerá en Swagger.
SPECTACULAR_SETTINGS = {

    "TITLE": "Sistema de Venta de Entradas",

    "DESCRIPTION": (
        "API REST para la gestión de eventos, "
        "recintos, sectores, carritos, compras y entradas."
    ),

    "VERSION": "1.0.0",

    # El esquema no incluye su propio endpoint.
    "SERVE_INCLUDE_SCHEMA": False,

    # Respaldo: cualquier vista de spectacular que no defina
    # sus propios permisos queda restringida a ORGANIZADOR/ADMIN.
    # Las vistas protegidas están en config/views.py.
    "SERVE_PERMISSIONS": ["usuarios.permissions.IsGestor"],

    # Evento y Compra tienen un campo "estado" con opciones
    # distintas; les damos nombres claros en el esquema.
    "ENUM_NAME_OVERRIDES": {
        "EstadoEventoEnum": "eventos.models.Evento.Estado",
        "EstadoCompraEnum": "compras.models.Compra.Estado",
    },

    # Swagger recuerda el token JWT ingresado en "Authorize"
    # al recargar la página.
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
    },
}