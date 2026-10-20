# Herbario Digital

Aplicacion compuesta por un frontend Angular 19, una API Django REST y PostgreSQL.
Docker Compose levanta los tres servicios; Nginx sirve Angular y enruta `/api/` al
backend. Las imagenes cargadas y los archivos estaticos de Django se almacenan en
volumenes persistentes.

## Requisitos

- Docker Engine y Docker Compose v2.

## Inicio rapido

1. Crea la configuracion local desde la plantilla:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Cambia `SECRET_KEY` y `DB_PASSWORD` en `.env`.
3. Construye y levanta los servicios:

   ```powershell
   docker compose up --build
   ```

La interfaz queda en <http://localhost:8080>, la API en <http://localhost:8080/api/>
y su documentacion en <http://localhost:8080/api/docs/>. El backend aplica las
migraciones y recopila los archivos estaticos al iniciar.

Para detener los servicios sin borrar los datos:

```powershell
docker compose down
```

Los datos de PostgreSQL, las imagenes y los archivos estaticos permanecen en los
volumenes `postgres_data`, `media_data` y `static_data`. Para borrarlos
intencionalmente, ejecuta `docker compose down --volumes`; esta accion elimina
los datos persistidos.

## Revision de la estructura

- `Herbario_frontend/`: aplicacion Angular, compilada como sitio estatico y servida
  por Nginx.
- `Herbario_backend/`: API Django REST; Gunicorn sirve la aplicacion WSGI.
- `docker-compose.yml`: servicios, dependencias, comprobaciones de salud y volumenes.
- El navegador usa la ruta relativa `/api`, por lo que no requiere una URL de API
  distinta ni CORS para el uso normal a traves de Nginx.

La configuracion incluida esta pensada como punto de partida local. Antes de un
despliegue publico configura secretos seguros, dominios y HTTPS.
