# Herbario Digital API

API REST para la gestion de un herbario digital. El proyecto esta construido con
Django, Django REST Framework, autenticacion JWT, PostgreSQL y documentacion
OpenAPI con Swagger.

## Requisitos

- Python 3.13
- PostgreSQL
- PowerShell

## Configuracion inicial

Crear y activar el entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements\dev.txt
```

Crear el archivo de variables de entorno:

```powershell
Copy-Item .env.example .env
```

Editar `.env` con los datos reales de la base PostgreSQL:

```env
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.postgresql
DB_NAME=herbario
DB_USER=herbario
DB_PASSWORD=herbario
DB_HOST=localhost
DB_PORT=5432
```

## Base de datos

Crear la base de datos en PostgreSQL antes de correr migraciones. Por defecto el
proyecto espera una base llamada `herbario`.

Aplicar migraciones:

```powershell
python src\manage.py migrate
```

Tambien puedes usar el script incluido:

```powershell
.\scripts\migrate_db.ps1
```

## Ejecutar el servidor

```powershell
python src\manage.py runserver 8000
```

La API quedara disponible en:

```text
http://127.0.0.1:8000/
```

## Endpoints principales

- `GET /api/docs/`: documentacion Swagger.
- `GET /api/schema/`: esquema OpenAPI.
- `POST /api/token/`: login y generacion de tokens JWT.
- `POST /api/token/refresh/`: refrescar token JWT.
- `/api/users/`: usuarios.
- `/api/roles/`: roles.
- `/api/taxonomy/`: taxonomia.
- `/api/taxonomy/statuses/`: catalogo de estados de conservacion.
- `/api/taxonomy/conservation-statuses/`: relacion entre especies y estados.
- `/api/collectors/`: colectores.
- `/api/locations/`: ubicaciones.
- `/api/specimens/`: especimenes.
- `/api/media/`: imagenes asociadas.
- `/api/collections/`: colecciones.

## Tests y calidad de codigo

Ejecutar tests:

```powershell
pytest
```

Ejecutar linter:

```powershell
ruff check .
```

Formatear codigo:

```powershell
black .
```

## Estructura del proyecto

```text
requirements/          Dependencias base y de desarrollo.
scripts/               Scripts auxiliares del proyecto.
src/manage.py          Entrada principal de Django.
src/config/            Configuracion global, URLs y settings.
src/apps/              Aplicaciones Django del dominio.
```

## Notas

- El archivo `.env` contiene configuracion sensible y no debe subirse a Git.
- Los archivos `.log`, caches y `.sqlite3` son archivos locales/generados.
- Aunque el proyecto tiene fallback a SQLite si falta `DB_ENGINE`, la configuracion
  actual usa PostgreSQL mediante `.env`.
