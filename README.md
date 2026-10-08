# 🎟 Butaca · Sistema de Venta de Entradas

Sistema de venta de entradas para eventos y conciertos.
Backend en **Django REST Framework + PostgreSQL** con autenticación **JWT por roles**, carro persistente, checkout transaccional con control de stock y entradas con código **UUID**. Frontend en **React (Vite)**.

**Alumno:** Daniel Alejandro Aceitón Sepúlveda · **Sección:** 2026/P TI3041/IEC-N4-C1/D Temuco IEC · **Año:** 2026

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.14, Django 5.2, Django REST Framework |
| Base de datos | PostgreSQL (`django.db.backends.postgresql`) |
| Autenticación | SimpleJWT (access + refresh, claim `rol`) |
| Filtros | django-filter, SearchFilter, OrderingFilter |
| Documentación | drf-spectacular (OpenAPI 3 / Swagger) |
| Frontend | React 19 + Vite, React Router |

## Instalación

### 1. Backend

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Crear la base de datos en PostgreSQL (por ejemplo `venta_entradas`) y copiar `.env.example` como `.env` con los datos de conexión y una `SECRET_KEY`.

```powershell
python manage.py migrate
python manage.py createsuperuser      # acceso a /admin/
python manage.py poblar_demo          # datos de demostración (opcional)
python manage.py runserver
```

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Abrir **http://localhost:5173**. Vite reenvía `/api` y `/media` al backend (puerto 8000).

### Usuarios de demostración (`poblar_demo`)

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador (ORGANIZADOR) | `admin_demo` | `Butaca-2026` |
| Espectador | `fan_demo` | `Butaca-2026` |

## Roles y permisos (RBAC)

| Endpoint | Público | Espectador | Administrador |
|---|:-:|:-:|:-:|
| `GET /api/eventos/` (solo PROGRAMADOS) | ✔ | ✔ | sus eventos |
| `POST/PATCH/DELETE /api/eventos/…` | | | ✔ |
| `GET/POST/DELETE /api/carro-tickets/` | | ✔ | |
| `POST /api/compras/pagar/` | | ✔ | |
| `GET /api/mis-entradas/` | | ✔ | |
| `PATCH /api/compras/{id}/estado/` | | | ✔ |
| `PATCH /api/eventos/sectores/{id}/` (stock) | | | ✔ |
| `GET /api/compras/resumen/` | | | ✔ |
| `/api/docs/` y `/api/schema/` (Swagger) | | | ✔ |

Permisos personalizados en `usuarios/permissions.py`: `IsEspectador`, `IsOrganizador`, `IsGestor`.

## Flujo de compra y stock

1. **Carrito** (`carrito`): relación 1:1 `Usuario ↔ Carrito` en PostgreSQL. Agregar ítems **no descuenta stock** y los ítems persisten tras cerrar sesión.
2. **Checkout** (`POST /api/compras/pagar/`), dentro de `transaction.atomic()`:
   - bloquea el carrito y los sectores con `select_for_update()`;
   - valida el stock (si no alcanza, rechaza y no modifica nada);
   - crea la orden `PENDIENTE`, descuenta el stock y genera una `Entrada` con `uuid4` por ticket;
   - cambia la orden a `PAGADO` y vacía el carrito.
3. **Cancelación** (`PATCH /api/compras/{id}/estado/`): `PAGADO → CANCELADO` **repone el stock** automáticamente.

Estados: `PENDIENTE → PAGADO → ENTREGADO` o `CANCELADO` (estados finales: ENTREGADO y CANCELADO).

## Filtros (django-filter)

```
GET /api/eventos/?categoria=CONCIERTO&precio_max=30000&con_stock=true
GET /api/eventos/?fecha_desde=2026-10-01&fecha_hasta=2026-12-31&ordering=-fecha
GET /api/eventos/?search=arena
GET /api/eventos/{id}/sectores/?disponible=true&precio_min=10000
GET /api/compras/?estado=PAGADO&evento=2
GET /api/mis-entradas/?evento=2&utilizada=false
```

Definidos en `eventos/filters.py`, `compras/filters.py` y `entradas/filters.py`.

## URLs principales

| URL | Descripción |
|---|---|
| http://localhost:5173 | Sitio del espectador |
| http://localhost:5173/panel | Panel del administrador |
| http://127.0.0.1:8000 | Portada de la API |
| http://127.0.0.1:8000/api/docs/ | Swagger (solo administradores) |
| http://127.0.0.1:8000/admin/ | Panel Django |

## Pruebas

```powershell
python manage.py test
```

Cubren carrito persistente, checkout y stock, cancelación con reposición, RBAC, filtros, registro, documentación protegida y páginas HTML.

## Instalación y configuración

1. Clonar el repositorio: git clone https://github.com/DaniAce21/Sistema-de-ventas.git
2. Crear entorno virtual e instalar dependencias: pip install -r requirements.txt
3. Copiar .env.example a .env y completar: SECRET_KEY, DEBUG, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
4. Aplicar migraciones: python manage.py migrate
5. Crear superusuario: python manage.py createsuperuser
6. Ejecutar servidor: python manage.py runserver

## Variables de entorno

El proyecto lee configuración sensible desde .env. Nunca comitees este archivo. Usa .env.example como plantilla.