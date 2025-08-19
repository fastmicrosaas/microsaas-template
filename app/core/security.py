from typing import Optional
from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import SessionLocal, get_db
from app.models.models import User
from app.services.auth.token_service import TokenService
from app.services.users.user_service import UserService
from app.core.database import SessionLocal
from app.models.models import SecurityLog
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from fastapi import Path
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    email = None

    if token:
        payload = TokenService.decode_token(token)
        email = payload.get("sub") if payload else None

    if not email and refresh_token:
        payload = TokenService.decode_token_or_raise(refresh_token, token_type="refresh")
        email = payload.get("sub")

    if not email:
        raise HTTPException(status_code=401, detail="Token no válido o expirado")

    user = UserService.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user

def get_current_user_optional(request: Request) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    payload = TokenService.decode_token(token)
    email = payload.get("sub") if payload else None
    
    if not email:
        return None

    db = SessionLocal()
    try:
        user = UserService.get_by_email(db, email)
        if user:
            request.state.user = user
        return user
    finally:
        db.close()

async def log_security_event(user_id, ip_address, event_type, description=None):
    db = SessionLocal()
    try:
        log = SecurityLog(
            user_id=user_id,
            ip_address=ip_address,
            event_type=event_type,
            description=description
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def ownership_dependency(model, id_param: str):
    def dependency(
        id_value: int = Path(..., alias=id_param),  
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        instance = db.query(model).filter(model.id == id_value).first()
        if not instance or instance.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este recurso.")
        return instance
    return dependency
