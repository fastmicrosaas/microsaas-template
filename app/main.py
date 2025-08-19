import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.security import limiter
from app.core.database import Base, engine
from app.core.hooks.audit import register_audit_listeners
from app.core.presentation.error_handlers import ErrorHandler
from app.core.middlewares.auth_middleware import AuthMiddleware
from app.core.middlewares.logging_middleware import LoggerMiddleware
from app.core.middlewares.security_middleware import CSRFMiddleware, SecureHeadersMiddleware
from app.models.models import User, Item, Plan, Order
from app.routes import auth, home, items, dashboard, mailing, payments, orders, settings, compliance
from app.api import contact
from app.seeders.seed_data import create_free_plan_if_not_exists
from fastapi.middleware.cors import CORSMiddleware  

# Config
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "public", "static")


def create_app() -> FastAPI:
    app = FastAPI(
        docs_url=None if IS_PRODUCTION else "/docs",
        redoc_url=None if IS_PRODUCTION else "/redoc",
        openapi_url=None if IS_PRODUCTION else "/openapi.json"
    )
    
    app.state.limiter = limiter

    # DB y auditoría
    Base.metadata.create_all(bind=engine)
    register_audit_listeners([User, Item, Plan, Order])

    # Static files
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Middleware
    register_middlewares(app)

    # Routes
    register_routes(app)

    # APIs
    register_api(app)

    # Error Handlers
    ErrorHandler.register(app)

    # Seed
    create_free_plan_if_not_exists()

    return app


def register_middlewares(app: FastAPI):
    app.add_middleware(SecureHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8000", "http://localhost:4321"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AuthMiddleware)
    app.add_middleware(LoggerMiddleware)
    app.add_middleware(CSRFMiddleware)


def register_routes(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(items.router)
    app.include_router(home.router)
    app.include_router(dashboard.router)
    app.include_router(mailing.router)
    app.include_router(payments.router)
    app.include_router(orders.router)
    app.include_router(settings.router)
    app.include_router(compliance.router)


def register_api(app: FastAPI):
    app.include_router(contact.router)


app = create_app()
