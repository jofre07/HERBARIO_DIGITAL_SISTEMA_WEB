from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = config("SECRET_KEY", default="change-me")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "apps.common",
    "apps.roles",
    "apps.users",
    "apps.taxonomy",
    "apps.collectors",
    "apps.locations",
    "apps.specimens",
    "apps.media",
    "apps.collections_app",
    "apps.site_content",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:4200,http://127.0.0.1:4200",
    cast=Csv(),
)

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DB_ENGINE = config("DB_ENGINE", default="django.db.backends.sqlite3")

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": config("DB_NAME", default=BASE_DIR / "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
        }
    }
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "es-ec"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
INITIAL_ADMIN_USERNAME = config("INITIAL_ADMIN_USERNAME", default="admin")
INITIAL_ADMIN_EMAIL = config("INITIAL_ADMIN_EMAIL", default="admin@example.com")
INITIAL_ADMIN_PASSWORD = config("INITIAL_ADMIN_PASSWORD", default=None)
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("apps.common.api.responses.StandardJSONRenderer",),
    "EXCEPTION_HANDLER": "apps.common.api.responses.standard_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticatedOrReadOnly",),
    "DEFAULT_FILTER_BACKENDS": ("rest_framework.filters.SearchFilter",),
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_RATES": {"public_searches": "60/hour"},
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Herbario Digital API",
    "DESCRIPTION": (
        "API REST del Herbario Digital: taxonomia, especimenes, ubicaciones, " "mapa y catalogo."
    ),
    "VERSION": "1.0.0",
    "TAGS": [
        {"name": "Autenticacion", "description": "Login, refresh token y seguridad."},
        {"name": "Sistema", "description": "Salud del servicio y estadisticas generales."},
        {"name": "Usuarios", "description": "Usuarios y asignacion interna de roles."},
        {"name": "Roles", "description": "Gestion del catalogo de roles."},
        {"name": "Taxonomia", "description": "Familias, generos, especies y catalogo."},
        {"name": "Colectores", "description": "Gestion de colectores."},
        {"name": "Ubicaciones", "description": "Ubicaciones, habitat, clima y mapa."},
        {"name": "Especimenes", "description": "Gestion y busqueda de especimenes."},
        {"name": "Imagenes", "description": "Imagenes asociadas a especimenes."},
        {"name": "Colecciones", "description": "Colecciones de especimenes."},
        {"name": "Contenido", "description": "Contenido editable del sitio publico."},
        {"name": "Documentacion", "description": "Schema OpenAPI y Swagger UI."},
    ],
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("ACCESS_TOKEN_MINUTES", default=60, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("REFRESH_TOKEN_DAYS", default=1, cast=int)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
