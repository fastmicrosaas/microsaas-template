from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.core.config import get_settings

settings = get_settings()

# Servicios de pagos disponibles
from app.services.payments.izipay_service import (
    create_izipay_checkout,
    handle_izipay_paid,
    handle_izipay_ipn,
    cleanup_pending_orders,
)

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/checkout", response_class=HTMLResponse)
async def checkout(
    request: Request,
    plan: str = Query(..., description="Nombre del plan"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if settings.PAYMENT_GATEWAY == "izipay":
        return await create_izipay_checkout(request, plan, db, current_user)
    raise HTTPException(status_code=400, detail="Método de pago no soportado")


@router.post("/paid", response_class=HTMLResponse)
async def paid(
    request: Request,
    kr_answer: str = Form(..., alias="kr-answer"),
    kr_hash: str = Form(..., alias="kr-hash"),
    db: Session = Depends(get_db),
):
    if settings.PAYMENT_GATEWAY == "izipay":
        return await handle_izipay_paid(request, kr_answer, kr_hash, db)
    raise HTTPException(status_code=400, detail="Método de pago no soportado")


@router.post("/ipn")
async def ipn(request: Request):
    if settings.PAYMENT_GATEWAY == "izipay":
        return await handle_izipay_ipn(request)
    raise HTTPException(status_code=400, detail="Método de pago no soportado")
