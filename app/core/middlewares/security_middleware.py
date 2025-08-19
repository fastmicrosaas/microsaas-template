from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import get_current_user_optional
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from typing import Callable
from app.core.security import log_security_event

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
EXEMPT_PATHS = [
    "/payments/paid",   # Izipay success return
    "/payments/ipn",    # Izipay webhook 
    "/consents",    # Izipay webhook 
]

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Si es un método seguro o una ruta exenta, dejar pasar
        if request.method in SAFE_METHODS or path in EXEMPT_PATHS:
            return await call_next(request)

        # Si es método sensible, verificar CSRF sólo si hay usuario autenticado
        user = get_current_user_optional(request)
        if user:
            token = request.headers.get("x-csrf-token")
            session_token = request.cookies.get("csrf_token")
            print("TOKENS", token, session_token)

            if not token or not session_token or token != session_token:
                print("CSRF FALLÓ", token, session_token)
                await log_security_event(user.id, request.client.host, "csrf_failed", f"CSRF token inválido en {path}")

                raise HTTPException(status_code=403, detail="CSRF token inválido o ausente")

        return await call_next(request)


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        path = request.url.path

        # Política CSP: checkout necesita más permisividad (Izipay)
        if path.startswith("/payments/checkout"):
            response.headers["Content-Security-Policy"] = (
                        "default-src 'self'; "
                        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://static.micuentaweb.pe https://secure.micuentaweb.pe https://h.online-metrix.net https://*.online-metrix.net; "
                        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://static.micuentaweb.pe https://cdn.jsdelivr.net; "
                        "img-src 'self' data: https://img.icons8.com https://cdn.jsdelivr.net https://static.micuentaweb.pe https://h.online-metrix.net https://*.online-metrix.net; "
                        "font-src 'self' https://fonts.gstatic.com; "
                        "frame-src https://secure.micuentaweb.pe https://static.micuentaweb.pe https://h.online-metrix.net https://*.online-metrix.net; "
                        "connect-src 'self' https://secure.micuentaweb.pe https://h.online-metrix.net https://*.online-metrix.net; "
                        "object-src 'none';"
                    )
            response.headers["Permissions-Policy"] = "payment=(self https://secure.micuentaweb.pe)"
        # === 2. Documentación (Swagger UI) ===
        elif path.startswith("/docs") or path.startswith("/redoc"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com; "
                "object-src 'none';"
            )

        else:
            # Política CSP estricta para el resto del sitio
            response.headers["Content-Security-Policy"] = (
                "default-src 'self' https://www.google.com/recaptcha/; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.twind.style/ https://cdn.tailwindcss.com https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/ https://www.gstatic.com/recaptcha/; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "img-src 'self' data: https://img.icons8.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com; "
                "object-src 'none';"
            )
            # COOP / COEP para aislamiento de origen ===
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Embedder-Policy"] = "same-origin"

        # Seguridad HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        # Evitar sniffing de tipos MIME
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Protección contra clickjacking
        response.headers["X-Frame-Options"] = (
            "ALLOW-FROM https://secure.micuentaweb.pe"
            if path.startswith("/payments/checkout") else
            "DENY"
        )

        # Política de referer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Nueva: Permissions Policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), gyroscope=(), geolocation=(), microphone=(), payment=(), usb=()"
        )



        return response