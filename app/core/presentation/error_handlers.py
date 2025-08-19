import traceback
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded
from app.core.presentation.templates import templates
import os

IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"


class ErrorHandler:
    @staticmethod
    def register(app: FastAPI):
        """Registra todos los manejadores de errores en la app"""
        app.add_exception_handler(StarletteHTTPException, ErrorHandler.http_exception_handler)
        app.add_exception_handler(RateLimitExceeded, ErrorHandler.rate_limit_handler)
        app.add_exception_handler(Exception, ErrorHandler.internal_exception_handler)

    @staticmethod
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return templates.TemplateResponse(
                "errors/404.html", {"request": request}, status_code=404
            )
        return await http_exception_handler(request, exc)

    @staticmethod
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": "Demasiadas peticiones, intenta más tarde"},
        )

    @staticmethod
    async def internal_exception_handler(request: Request, exc: Exception):
        if not IS_PRODUCTION:
            print("Error interno:", traceback.format_exc())

        return templates.TemplateResponse(
            "errors/500.html", {"request": request}, status_code=500
        )
