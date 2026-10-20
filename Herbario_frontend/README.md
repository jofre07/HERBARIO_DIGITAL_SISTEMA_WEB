# Herbario Digital

Herbario Digital es la aplicación web para consultar y administrar la colección de un herbario. Este repositorio contiene el **frontend**: una interfaz pública para explorar especies, especímenes, imágenes, colecciones y ubicaciones, y un panel administrativo para mantener esos datos y gestionar el acceso de los usuarios.

El frontend está construido con Angular y se comunica por HTTP con una API externa. No contiene la base de datos ni la lógica del servidor.

## Requisitos

- Node.js y npm compatibles con la versión de Angular CLI del proyecto.
- La API del sistema disponible para que funcionen las consultas y operaciones de datos.

## Instalación y ejecución

Desde la raíz del proyecto:

```bash
npm install
npm start
```

`npm start` ejecuta Angular en modo desarrollo y abre la aplicación en el navegador. Para compilar:

```bash
npm run build
```

Para ejecutar las pruebas unitarias:

```bash
npm test
```

## Configuración de la API

La dirección base de la API se define en los archivos de entorno:

- Desarrollo: `src/environments/environment.development.ts`, por defecto `http://127.0.0.1:8000/api`.
- Producción: `src/environments/environment.ts`, por defecto `/api`.

En desarrollo, la API debe estar disponible en la dirección configurada. En producción, el servidor que aloja el frontend debe enrutar `/api` al backend correspondiente.

## Cómo funciona

1. Angular inicia la aplicación desde `src/main.ts` y carga las rutas configuradas en `src/app/app.routes.ts`.
2. Las páginas y módulos solicitan datos a los servicios del dominio. Estos usan `HttpClient` y la URL configurada en el entorno para comunicarse con la API.
3. Los servicios convierten las respuestas de la API a los modelos e interfaces definidos en `src/app/core/interfaces`.
4. La zona pública consulta los endpoints públicos. Las operaciones del panel administrativo requieren una sesión válida y, según la sección, los permisos necesarios.
5. Las listas administrativas y públicas presentan datos paginados; los módulos que lo ofrecen también permiten búsqueda y filtros.

### Acceso y permisos

- El inicio de sesión se realiza en `/login` contra el endpoint de tokens de la API.
- Al iniciar sesión, el frontend guarda el token de acceso, el token de renovación y los datos del usuario en `localStorage`.
- El `authInterceptor` agrega el token de acceso a las solicitudes HTTP y, ante una respuesta `401`, limpia la sesión y redirige al inicio de sesión.
- `authGuard` protege el área `/admin`; `permissionGuard` restringe las rutas administrativas según el permiso declarado por cada ruta.
- La interfaz también oculta acciones para las que el usuario no tiene permiso. La autorización definitiva debe aplicarse igualmente en el backend.

## Módulos de la aplicación

### Sitio público

Las páginas públicas comparten la estructura de encabezado y pie de página definida en `src/app/public/layout`.

| Página | Función |
| --- | --- |
| Inicio (`/`) | Presenta información destacada, estadísticas, búsquedas frecuentes y un acceso rápido a la búsqueda del catálogo. |
| Catálogo (`/catalogo`) | Explora especies con filtros por nombre, familia, género, estado de conservación, ubicación, clima y hábitat; permite cambiar la vista y paginar resultados. |
| Detalle del catálogo (`/catalogo/:id`) | Muestra la ficha de una especie y su información relacionada. |
| Especímenes (`/especimenes`) | Permite consultar los especímenes publicados. |
| Búsqueda avanzada (`/busqueda-avanzada`) | Busca especímenes combinando criterios taxonómicos, nombre común, colector, ubicación, conservación, hábitat y clima. |
| Mapa (`/mapa`) | Visualiza puntos geográficos asociados a especímenes. Usa Leaflet, mapas base de OpenStreetMap y el límite geográfico de Manabí disponible en `public/data/manabi.geojson`. |
| Galería (`/galeria`) | Explora imágenes públicas con filtros y paginación; permite ampliar imágenes en un visor. |
| Colecciones (`/colecciones`) | Consulta colecciones públicas y las filtra por categoría, conservación, familia y ubicación. |
| Acerca de (`/acerca`) | Presenta información institucional y contenido descriptivo del herbario. |

### Panel administrativo

El panel usa el diseño de `src/app/layout/main-layout` y requiere autenticación. Las rutas administrativas están bajo `/admin`.

| Área | Función |
| --- | --- |
| Panel (`/admin/dashboard`) | Muestra el resumen estadístico y los indicadores del herbario. |
| Perfil (`/admin/perfil`) | Presenta la información del usuario autenticado. |
| Usuarios (`/admin/usuarios`) | Busca, pagina, crea, edita y elimina usuarios; permite asignar roles. |
| Roles (`/admin/roles`) | Administra roles y los permisos asociados. |
| Familias (`/admin/taxonomia/familias`) | Mantiene el catálogo taxonómico de familias. |
| Géneros (`/admin/taxonomia/generos`) | Mantiene géneros y su relación con familias. |
| Especies (`/admin/taxonomia/especies`) | Mantiene especies y su relación con géneros; permite marcar especies destacadas. |
| Estados taxonómicos (`/admin/taxonomia/estados`) | Administra el catálogo de estados utilizado por la taxonomía. |
| Nombres comunes (`/admin/taxonomia/nombres-comunes`) | Gestiona nombres comunes asociados a especies. |
| Traducciones (`/admin/taxonomia/traducciones`) | Administra las traducciones vinculadas a la información taxonómica. |
| Estados de conservación (`/admin/taxonomia/estados-conservacion`) | Mantiene los estados de conservación de las especies. |
| Climas (`/admin/climas`) y hábitats (`/admin/habitats`) | Gestiona los catálogos ambientales usados para describir las ubicaciones y los especímenes. Ambos reutilizan el mismo componente configurable. |
| Colectores (`/admin/colectores`) | Mantiene los datos de las personas colectoras. |
| Especímenes (`/admin/especimenes`) | Administra registros de especímenes, publicación, especie, colector y una o más ubicaciones con coordenadas y datos ambientales. |
| Imágenes (`/admin/imagenes`) | Asocia imágenes a especímenes, permite administrar sus créditos y vistas previas; el componente limita cada espécimen a cinco imágenes y acepta JPG, PNG y WebP de hasta 10 MB. |
| Colecciones (`/admin/colecciones`) | Administra las colecciones del herbario. |
| Contenido de “Acerca de” (`/admin/contenido/acerca`) | Edita el contenido institucional público, incluyendo introducción, misión, visión, equipo, contacto e imagen. |

Las rutas administrativas especifican los permisos requeridos en `src/app/app.routes.ts`. Existe también un componente para administrar ubicaciones (`src/app/features/locations/locations.component.ts`), pero no está registrado como ruta en la configuración actual.

### Módulos transversales

- **`core/services`**: acceso a la API por dominio. Incluye autenticación, taxonomía, especímenes, imágenes, colecciones, colectores, ubicaciones, catálogos ambientales, usuarios, roles, estadísticas, opciones de filtros y contenido institucional.
- **`core/interfaces`**: tipos de datos y contratos de respuesta compartidos por páginas y servicios.
- **`core/guards` e `interceptors`**: control de acceso a rutas y configuración de solicitudes HTTP autenticadas.
- **`components`**: elementos reutilizables como formularios y modales, tablas, búsqueda, paginación, selectores, confirmaciones, breadcrumbs y visor de imágenes.
- **`shared`**: utilidades y elementos compartidos, por ejemplo validación de formularios, alertas, directivas, textos de interfaz y creación de marcadores del mapa.
- **`public/i18n`**: recursos de textos de interfaz en español.

## Tecnologías principales

- Angular 19 y TypeScript.
- Angular Router, formularios reactivos y `HttpClient`.
- RxJS para el manejo de solicitudes y flujos de datos.
- Bootstrap 5, Bootstrap Icons y estilos propios.
- Leaflet para la visualización de mapas.
- SweetAlert2 para alertas y confirmaciones.
