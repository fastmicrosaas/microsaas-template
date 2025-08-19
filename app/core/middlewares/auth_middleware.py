from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse
from app.core.security import log_security_event
from app.core.presentation.templates import templates
from app.core.context import set_current_user_id
from app.services.auth.token_service import TokenService
from app.services.users.user_service import UserService
from app.services.plans.plan_service import PlanService
from app.services.routing.route_guard_service import RouteGuard

 
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        user = None
        ip = request.client.host

        # Obtener usuario si token válido
        username = TokenService.get_subject_from_token(token)
        if username:
            user = UserService.get_user_by_email(username)
            if user:
                set_current_user_id(user.id)

        # Si no hay access_token pero sí refresh, renovar
        if not user and refresh_token and not path.startswith("/auth/logout"):
            username = TokenService.get_subject_from_token(refresh_token)
            if username:
                user = UserService.get_user_by_email(username)
                if user:
                    new_token = TokenService.create_access_token({"sub": username})
                    request.state.renewed_token = new_token
                    set_current_user_id(user.id)

        # Redirigir si usuario ya autenticado e intenta ir a /login o /register
        if RouteGuard.is_auth_route(path) and user:
            return RedirectResponse(url="/dashboard")

        # Permitir rutas públicas
        if RouteGuard.is_public(path):
            response = await call_next(request)
            return self._add_renewed_token_if_needed(request, response)

        # Proteger rutas privadas
        if RouteGuard.is_protected(path):
            if not user:
                await log_security_event(None, ip, "unauthorized_access",
                        f"Intento acceso a {path} sin autenticación")
                return RedirectResponse(url="/auth/login")

            plan_status = PlanService.get_plan_status(user)

            if plan_status == "no_plan" and RouteGuard.should_block_plan_access(path):
                return RedirectResponse(url="/payments/checkout?plan=starter")

            if plan_status == "expired" and RouteGuard.should_block_plan_access(path):
                content = templates.get_template("errors/403.html").render({
                    "request": request,
                    "detail": "Tu plan ha expirado."
                })
                return HTMLResponse(content=content, status_code=403)

        # Continuar normalmente
        response = await call_next(request)
        return self._add_renewed_token_if_needed(request, response)

    def _add_renewed_token_if_needed(self, request, response):
        if hasattr(request.state, "renewed_token"):
            response.set_cookie(
                key="access_token",
                value=request.state.renewed_token,
                httponly=True,
                max_age=TokenService.token_expiry_seconds(),
                secure=True,
                samesite="lax"
            )
        return response
