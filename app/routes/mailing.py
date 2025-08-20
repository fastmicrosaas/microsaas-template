from fastapi import APIRouter, Cookie, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.services.mailing.mail_service import send_mail
from app.utils.recaptcha_util import verify_recaptcha
from app.core.presentation.templates import render_template
from app.core.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/mailing", tags=["Mailing"])

@router.post("/contact")
async def contact_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    g_recaptcha_response_contact: str = Form(...)
):
    print("Token recibido:", g_recaptcha_response_contact)

    if not await verify_recaptcha(g_recaptcha_response_contact, "contact"):
        raise HTTPException(status_code=400, detail="Fallo en reCAPTCHA")

    subject = f"Nuevo contacto de {name}"
    body = f"Nombre: {name}\nCorreo: {email}\n\nMensaje:\n{message}"
    reciever = settings.RECIEVER_EMAIL

    if send_mail(subject, body, to_email=reciever):
        response = RedirectResponse(url="/mailing/thankyou", status_code=303)
        response.set_cookie(key="contact_submitted", value="true", max_age=300)  # 5 min
        return response
    else:
        return RedirectResponse(url="/contact?error=1", status_code=303)


@router.get("/thankyou")
async def thankyou(request: Request, contact_submitted: str = Cookie(None)):
    if contact_submitted != "true":

        return RedirectResponse(url="/")

    response = render_template(request, "mailing/thankyou.html")
    response.delete_cookie("contact_submitted")
    return response
