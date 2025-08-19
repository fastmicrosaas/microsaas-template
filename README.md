# 🚀 Startup Project Starter Kit 

Un boilerplate **listo para producción** 

## 🧩 Funcionalidades clave

- **Backend rápido con FastAPI** – Arquitectura escalable y moderna.
- **UI lista para personalizar** – TailwindCSS + HTMX para una experiencia fluida y reactiva.
- **Render dinámico con Jinja2** – Reutiliza layouts y partials como en proyectos grandes.
- **Base de datos escalable con SQLAlchemy** – Modelos predefinidos para usuarios, planes, ítems y órdenes.
- **Seeders y datos iniciales** – Incluye un plan gratuito por defecto para onboarding inmediato.
- **Integración con pasarelas de pago** – Listo para conectar y procesar suscripciones o compras.
- **Autenticación segura** – Registro, login, logout y rutas protegidas con JWT.
- **Gestión de planes y suscripciones** – Control de expiración, upgrades y renovaciones.
- **Rate Limiting** – Protección contra abuso de la API.

## 🛡 Seguridad de nivel empresarial

- **Secure Headers** – Blindaje contra ataques comunes (XSS, clickjacking, etc.).
- **Protección CSRF** – Evita ataques de falsificación de solicitudes.
- **Middleware de autenticación** – Control total de acceso a recursos.
- **Validación estricta de inputs/outputs** – Con Pydantic.
- **Auditoría completa de datos** – Seguimiento de cambios en usuarios, planes, ítems y órdenes.
- **Paginación, filtros y búsqueda** – Previene sobrecarga y optimiza consultas.

## ⚙️ Listo para producción

- **Arquitectura modular** – Separación clara de core, rutas, middlewares, modelos, utilidades y seeders.
- **Entorno dev/prod separado** – Configuración limpia con `BaseSettings`.
- **CRUD completo** – Para usuarios, planes, ítems y órdenes.


Este proyecto usa [Alembic](https://alembic.sqlalchemy.org/) para gestionar migraciones de base de datos.

### Iniciar proyecto

```bash
 uvicorn app.main:app --reload
```

### 📦 Crear una nueva migración (autogenerada)

Después de hacer cambios en los modelos de SQLAlchemy:

```bash
alembic revision --autogenerate -m "agregué campo nuevo"
```

🚀 Aplicar las migraciones

```bash
alembic upgrade head
```

🔁 Deshacer una migración

```bash
alembic downgrade -1
```

### Escanear dependencias

```bash
pip install pip-audit safety bandit
```
Ejecutar:
```bash
bash scan_dependencies.sh
```

 