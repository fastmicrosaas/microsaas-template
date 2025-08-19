import requests
from app.core.config import get_settings

settings = get_settings()

RECAPTCHA_SECRET_KEY = settings.RECAPTCHA_SECRET_KEY

async def verify_recaptcha(token: str, action: str) -> bool:
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": RECAPTCHA_SECRET_KEY,
        "response": token
    }
    r = requests.post(url, data=data)
    result = r.json()
    return result.get("success") and result.get("action") == action and result.get("score", 0) >= 0.5
