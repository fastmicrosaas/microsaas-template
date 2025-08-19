import os
import secrets
from fastapi import Request, Response
from fastapi.templating import Jinja2Templates
from app.core.config import get_settings

settings = get_settings()

RECAPTCHA_SITE_KEY = settings.RECAPTCHA_SITE_KEY

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # app/

PUBLIC_DIR = os.path.join(BASE_DIR, "public")

TEMPLATES_DIR = os.path.join(PUBLIC_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.globals["RECAPTCHA_SITE_KEY"] = RECAPTCHA_SITE_KEY

def render_template(
    request: Request,
    template_name: str,
    context: dict = None,
    *,
    with_csrf: bool = False,
    csrf_cookie_secure: bool = True,
    csrf_samesite: str = "strict"
) -> Response:

    if context is None:
        context = {}
    context["request"] = request

    if with_csrf:
        csrf_token = secrets.token_urlsafe(32)
        context["csrf_token"] = csrf_token

        response = templates.TemplateResponse(template_name, context)
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,
            secure=csrf_cookie_secure,
            samesite=csrf_samesite,
            max_age=3600
        )
        return response

    return templates.TemplateResponse(template_name, context)
