import json
from math import ceil
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import HTMLResponse
from app.core.security import get_current_user
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Order, Plan, User, Item
from datetime import datetime, timedelta
import os
from app.core.presentation.templates import render_template
from app.core.security import limiter 

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Página principal del Dashboard
@router.get("/", response_class=HTMLResponse)
@limiter.limit("15/minute")
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item_count = db.query(Item).filter(Item.owner_id == current_user.id).count()
    order_count = db.query(Order).filter(Order.user_id == current_user.id).count()

    plan_info = get_user_plan_info(current_user, db)
    plan_name = plan_info["plan"].name if plan_info else "Sin plan"
    is_free_plan = plan_info["plan"].is_free if plan_info else True

    return render_template(request, "dashboard/index.html", {
        "user": current_user,
        "item_count": item_count,
        "order_count": order_count,
        "plan_name": plan_name,
        "is_free_plan": is_free_plan,
        **(plan_info or {})
    })

@router.get("/items", response_class=HTMLResponse)
def dashboard_items_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(Item).filter(Item.created_by == current_user.id).all()

    return render_template(
        request,
        "dashboard/items/index.html",
        {"items": items},
        with_csrf=True
    )

# Página de Órdenes dentro del Dashboard
@router.get("/orders", response_class=HTMLResponse)
def dashboard_orders(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = 1,
    per_page: int = 10,
):
    # Conteo total de órdenes del usuario
    total_orders = db.query(Order).filter(Order.user_id == current_user.id).count()
    total_pages = ceil(total_orders / per_page)

    # Obtener solo las órdenes para la página actual
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.id.desc())  # opcional, por ejemplo mostrar más recientes primero
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return render_template(request, "dashboard/orders/index.html", {
        "orders": orders,
        "page": page,
        "total_pages": total_pages,
    })

@router.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return render_template(request, "dashboard/profile/index.html", {
        "user": current_user
    })

@router.get("/privacy", response_class=HTMLResponse)
def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return render_template(
        request, 
        "dashboard/privacy/index.html",  
        {"user": current_user},
        with_csrf= True
    )

@router.get("/plans", response_class=HTMLResponse)
def user_plan_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan_info = get_user_plan_info(current_user, db)
    if not plan_info:
        raise HTTPException(status_code=404, detail="No se encontró información del plan")

    return render_template(request, "dashboard/plans/index.html", {
        "user": current_user,
        **plan_info
    })

def get_user_plan_info(user: User, db: Session) -> Optional[Dict]:
    if not user.plan_id or not user.plan_assigned_at:
        return None

    plan = db.query(Plan).filter(Plan.id == user.plan_id).first()
    if not plan:
        return None

    assigned_at = user.plan_assigned_at
    expiration_date = assigned_at + timedelta(days=plan.validity_days)
    now = datetime.utcnow()
    days_remaining = max((expiration_date - now).days, 0)

    alert = None
    if days_remaining == 0 and expiration_date < now:
        alert = "Tu plan ha vencido. Por favor, renueva tu suscripción para continuar usando el servicio."
    elif days_remaining <= 5:
        alert = f"Tu plan vencerá en {days_remaining} día(s). Considera renovarlo pronto."

    features = json.loads(plan.features) if isinstance(plan.features, str) else plan.features

    return {
        "plan": plan,
        "assigned_at": assigned_at,
        "expiration_date": expiration_date,
        "days_remaining": days_remaining,
        "alert": alert,
        "features": features
    }