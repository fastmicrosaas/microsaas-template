from datetime import datetime, timedelta
import re
from fastapi import HTTPException
from requests import Session

from app.models.models import User
from app.utils.constants import LOCK_TIME_MINUTES, MAX_FAILED_ATTEMPTS

def validate_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="La contraseña debe contener al menos una letra mayúscula.")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="La contraseña debe contener al menos una letra minúscula.")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="La contraseña debe contener al menos un número.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="La contraseña debe contener al menos un símbolo.")


# Comprueba bloqueo según campos de usuario (lock_until en DB)
def is_user_blocked(user: User) -> bool:
    return bool(user.lock_until and user.lock_until > datetime.utcnow())

# Registra un intento fallido y bloquea si alcanza el límite
def register_failed_attempt(db: Session, user: User):
    user.failed_attempts = (user.failed_attempts or 0) + 1
    if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
        user.lock_until = datetime.utcnow() + timedelta(minutes=LOCK_TIME_MINUTES)
        user.failed_attempts = 0  # reset tras bloqueo, opcional
    db.add(user)
    db.commit()
    db.refresh(user)

# Resetea contador tras login exitoso
def reset_attempts(db: Session, user: User):
    user.failed_attempts = 0
    user.lock_until = None
    db.add(user)
    db.commit()
    db.refresh(user)