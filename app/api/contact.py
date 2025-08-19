from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.mailing.mail_service import send_mail
from app.utils.recaptcha_util import verify_recaptcha
from app.core.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/api", tags=["Contact API"])

@router.post("/contact")
async def api_contact_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    g_recaptcha_response_contact: str = Form(...)
):
    print("Token recibido:", g_recaptcha_response_contact)

    # Verificar reCAPTCHA
    if not await verify_recaptcha(g_recaptcha_response_contact, "contact"):
        raise HTTPException(status_code=400, detail="Fallo en reCAPTCHA")

    # Datos del correo
    subject = f"Nuevo contacto de {name}"
    body = f"Nombre: {name}\nCorreo: {email}\n\nMensaje:\n{message}"
    receiver = settings.RECIEVER_EMAIL

    # Enviar correo
    if send_mail(subject, body, to_email=receiver):
            return HTMLResponse(
                content='<span class="text-green-400">✅ Mensaje enviado correctamente</span>'
            )
    else:
            return HTMLResponse(
                content='<span class="text-red-400">❌ No se pudo enviar el mensaje</span>',
                status_code=500
            )
