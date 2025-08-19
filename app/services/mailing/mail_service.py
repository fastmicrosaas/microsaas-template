import smtplib
import ssl
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings

settings = get_settings()

SMTP_PROVIDERS = {
    "gmail": {
        "host": settings.SMTP_HOST_GMAIL,
        "port": int(settings.SMTP_PORT_GMAIL),
        "user": settings.SMTP_USER_GMAIL,
        "pass": settings.SMTP_PASS_GMAIL
    },
    "hostinger": {
        "host": settings.SMTP_HOST_HOSTINGER,
        "port": int(settings.SMTP_PORT_HOSTINGER),
        "user": settings.SMTP_USER_HOSTINGER,
        "pass": settings.SMTP_PASS_HOSTINGER
    }
}

provider = (settings.SMTP_PROVIDER or "").lower()
if provider not in SMTP_PROVIDERS:
    raise ValueError(f"Proveedor SMTP '{provider}' no soportado.")

cfg = SMTP_PROVIDERS[provider]

def _sanitize(v: str) -> str:
    if v is None:
        return ""

    return v.strip().strip("'").strip('"')

cfg["host"] = _sanitize(cfg["host"])
cfg["user"] = _sanitize(cfg["user"])
cfg["pass"] = _sanitize(cfg["pass"])
# port is int already

def send_mail(subject: str, body: str, to_email: str, html: bool = False):
    try:
        msg = MIMEMultipart()
        msg["From"] = cfg["user"]
        msg["To"] = to_email
        msg["Subject"] = subject
        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        # debug output
        print(f"[mail] provider={provider} host={cfg['host']} port={cfg['port']} user={cfg['user']}")

        # Use SSL for port 465
        if cfg["port"] == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=context, timeout=15) as server:
                server.set_debuglevel(1)  # imprime diálogo SMTP
                server.login(cfg["user"], cfg["pass"])
                server.sendmail(cfg["user"], to_email, msg.as_string())
        else:
            # STARTTLS flow for ports like 587
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as server:
                server.set_debuglevel(1)
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
                server.login(cfg["user"], cfg["pass"])
                server.sendmail(cfg["user"], to_email, msg.as_string())

        print(f"[OK] Email enviado usando {provider}")
        return True

    except Exception as e:
        print(f"[ERROR] Fallo enviando email con {provider}: {e}")
        traceback.print_exc()
        return False
