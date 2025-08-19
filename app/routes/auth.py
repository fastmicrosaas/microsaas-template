from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from jose import jwt, JWTError
from app.core.security import (
    ALGORITHM,
    SECRET_KEY 
)
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import log_security_event
from app.models.models import User, Plan, ConsentLog
from datetime import datetime
from app.core.config import get_settings
from app.services.auth.password_service import PasswordService
from app.services.auth.token_service import TokenService
from app.core.security import limiter 
from app.utils.auth_utils import is_user_blocked, register_failed_attempt, reset_attempts, validate_password_strength
from app.utils.constants import DPA_DESCRIPTION, MARKETING_DESCRIPTION
from app.utils.recaptcha_util import verify_recaptcha
from app.core.presentation.templates import render_template

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Auth"])

# ---- LOGIN ----
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render_template(request, "auth/login.html")

@router.post("/login")
@limiter.limit("7/5minute") 
async def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    g_recaptcha_response: str = Form(...)
):
    print("Token recibido:", g_recaptcha_response)

    if not await verify_recaptcha(g_recaptcha_response, "login"):
        await log_security_event(None, request.client.host, "recaptcha_failed", "Fallo en reCAPTCHA durante login")

        raise HTTPException(status_code=400, detail="Fallo en reCAPTCHA")
    
    # Busca usuario en BD

    user = db.query(User).filter(User.email == email).first()

    # Si existe y está bloqueado -> mensaje con tiempo restante
    if user and is_user_blocked(user):
        minutos_restantes = int((user.lock_until - datetime.utcnow()).total_seconds() // 60) + 1
        return render_template(
            request,
            "auth/login.html",
            {"error": f"Cuenta bloqueada temporalmente. Intenta en {minutos_restantes} minutos."}
        )

    # Verificar existencia y contraseña
    if not user or not PasswordService.verify_password(password, user.hashed_password):
        # Si existe, registra intento en BD
        if user:
            register_failed_attempt(db, user)
            
        await log_security_event(user.id if user else None, request.client.host, "login_failed", f"Intento fallido para email: {email}")
   
        # Mensaje genérico para no filtrar si el email existe
        return render_template(
            request,
            "auth/login.html",
            {"error": "Credenciales inválidas"}
        )

    # Login correcto: resetear intentos y crear tokens
    reset_attempts(db, user)

    token = TokenService.create_access_token({"sub": user.email})
    refresh_token = TokenService.create_refresh_token({"sub": user.email})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60*60*24*settings.REFRESH_TOKEN_EXPIRE_DAYS,
        samesite="Lax",
        secure=True
    )
    return response

# ---- LOGOUT ----
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


# ---- REGISTER ----
@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return render_template(request, "auth/register.html")

@router.post("/register")
async def register_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    full_name: str = Form(...),
    last_name: str = Form(None),
    phone_number: str = Form(...),
    company: str = Form(None),
    job_title: str = Form(None),
    accept_dpa: bool = Form(...),   
    accept_marketing: Optional[str] = Form(None),  
    db: Session = Depends(get_db),
    g_recaptcha_response_register: str = Form(...),
):
    print("Token recibido:", g_recaptcha_response_register)

    if not await verify_recaptcha(g_recaptcha_response_register, "register"):
        raise HTTPException(status_code=400, detail="Fallo en reCAPTCHA")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return render_template(
            request,
            "auth/register.html",
            {"error": "El correo ya está registrado"}
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return render_template(
            request,
            "auth/register.html",
            {"error": "El correo ya está registrado"}
        )
    
    validate_password_strength(password)

    hashed_password = PasswordService.hash_password(password)
    new_user = User(
        email=email,
        full_name=full_name,
        last_name=last_name,
        phone_number=phone_number,
        company=company,
        job_title=job_title,
        hashed_password=hashed_password,
    )

        # 🔓 Asignar plan gratuito si está habilitado en el entorno
    if settings.HAS_FREE_DEMO and settings.FREE_PLAN_NAME:
        free_plan = db.query(Plan).filter_by(name=settings.FREE_PLAN_NAME, is_free=True).first()
        if free_plan:
            new_user.plan = free_plan
            new_user.plan_assigned_at = datetime.utcnow()
            
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Guardar consentimiento obligatorio (DPA + Términos)
    dpa_consent = ConsentLog(
        user_id=new_user.id,
        policy_type="dpa_terms",
        version="1.0",   
        description=DPA_DESCRIPTION.strip(),
        accepted=True,
        ip_address=request.client.host
    )
    db.add(dpa_consent)

    # Guardar consentimiento opcional (marketing)
    if accept_marketing:
        marketing_consent = ConsentLog(
            user_id=new_user.id,
            policy_type="marketing",
            version="1.0",
            description=MARKETING_DESCRIPTION.strip(),
            accepted=True,
            ip_address=request.client.host
        )
        db.add(marketing_consent)

    db.commit()

    token = TokenService.create_access_token({"sub": new_user.email})
    refresh_token = TokenService.create_refresh_token({"sub": new_user.email})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=7*24*60*60)  # 7 días
    return response


@router.post("/refresh")
def refresh_access_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    print("REFRESH TOKEN RECIBIDO:", refresh_token)
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token ausente")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token expired or invalid")
    
    user_email = TokenService._verify_refresh_token(refresh_token)
    if not user_email:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    new_access_token = TokenService.create_access_token({"sub": user_email})

    response = JSONResponse(content={"success": True})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=3600,
        secure=True,
        samesite="Lax"
    )
    return response
