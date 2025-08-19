
import base64
import hmac
import hashlib
import json
import secrets
import httpx
from datetime import datetime, timedelta
from urllib.parse import parse_qs
from fastapi.responses import HTMLResponse, RedirectResponse
from app.core.presentation.templates import templates
from app.core.config import get_settings

settings = get_settings()

IZIPAY_USERNAME = settings.IZIPAY_USERNAME
IZIPAY_PASSWORD = settings.IZIPAY_PASSWORD
IZIPAY_HMACSHA256 = settings.IZIPAY_HMACSHA256
IZIPAY_ENDPOINT = settings.IZIPAY_ENDPOINT
IZIPAY_PUBLIC_KEY = settings.IZIPAY_PUBLIC_KEY

from app.models.models import Order, OrderStatus, Plan, User
from sqlalchemy.orm import Session
from fastapi import Request


def build_auth_header() -> str:
    raw = f"{IZIPAY_USERNAME}:{IZIPAY_PASSWORD}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("utf-8")


def validate_kr_hash(kr_answer: str, kr_hash: str) -> bool:
    computed_hash = hmac.new(
        IZIPAY_HMACSHA256.encode("utf-8"),
        msg=kr_answer.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return secrets.compare_digest(kr_hash, computed_hash)

def extract_payment_uuid(query_string: str) -> str | None:
    params = parse_qs(query_string)
    return params.get("orderId", [None])[0]


def create_order(db: Session, user: User, plan_name: str) -> Order:
    plan = db.query(Plan).filter(Plan.name == plan_name).first()
    if not plan:
        raise ValueError(f"Plan '{plan_name}' no encontrado")

    order = Order(
        user_id=user.id,
        plan_id=plan.id,
        status=OrderStatus.PENDING,
        payment_reference=None,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def process_order_payment(answer: dict, db: Session):
    order_details = answer.get("orderDetails", {})
    order_id = order_details.get("orderId")
    payment_uuid = None

    transactions = answer.get("transactions", [])
    if transactions and isinstance(transactions, list):
        payment_uuid = transactions[0].get("uuid")

    if not order_id:
        return None

    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        # Marcar orden como pagada
        order.status = OrderStatus.PAID
        order.payment_reference = payment_uuid

        # Actualizar plan del usuario
        user = db.query(User).filter(User.id == order.user_id).first()
        user.plan_id = order.plan_id
        user.plan_assigned_at = datetime.utcnow()

        db.commit()
        db.refresh(order)
        return order
    return None


async def create_izipay_checkout(
    request: Request,
    plan: str,
    db: Session,
    current_user: User,
):
    if not current_user or not isinstance(current_user, User):
        return RedirectResponse(url="/auth/login", status_code=302)

    plan_obj = db.query(Plan).filter(Plan.name == plan).first()
    if not plan_obj:
        return HTMLResponse(f"Plan '{plan}' no encontrado", status_code=400)

    order = (
        db.query(Order)
        .filter(
            Order.user_id == current_user.id,
            Order.plan_id == plan_obj.id,
            Order.status == OrderStatus.PENDING,
        )
        .order_by(Order.id.desc())
        .first()
    )

    if not order:
        order = create_order(db, current_user, plan)

    izipay_order = {
        "amount":  int(plan_obj.price * 100), #decimal a entero - izipay
        "currency": "PEN",
        "orderId": order.id,
        "customer": {"email": current_user.email},
        "metadata": {"plan": plan},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{IZIPAY_ENDPOINT}/api-payment/V4/Charge/CreatePayment",
            headers={
                "Authorization": build_auth_header(),
                "Content-Type": "application/json",
            },
            json=izipay_order,
        )
        data = response.json()

    print("[DEBUG] Respuesta CreatePayment:", response.status_code, response.text)
    features = json.loads(plan_obj.features) if isinstance(plan_obj.features, str) else plan_obj.features

    if data.get("status") == "SUCCESS":
        formtoken = data["answer"]["formToken"]
        return templates.TemplateResponse(
            "payments/izipay/checkout.html",
            {
                "request": request,
                "formtoken": formtoken,
                "publickey": IZIPAY_PUBLIC_KEY,
                "endpoint": IZIPAY_ENDPOINT,
                "order_id": order.id,
                "plan": plan_obj,
                "features": features
            },
        )

    return HTMLResponse("Error al generar formToken", status_code=500)

async def handle_izipay_paid(request: Request, kr_answer: str, kr_hash: str, db: Session):
    if not validate_kr_hash(kr_answer, kr_hash):
        return templates.TemplateResponse(
            "payments/izipay/paid.html",
            {
                "request": request,
                "response": "Error en validación HMAC",
                "details": kr_answer,
            },
        )

    answer = json.loads(kr_answer)
    order = process_order_payment(answer, db)

    return templates.TemplateResponse(
        "payments/izipay/paid.html",
        {
            "request": request,
            "response": answer.get("orderStatus", "Desconocido"),
            "details": answer.get("orderDetails", {}),
            "order": order,
            "redirect_after": 5,
        },
    )


async def handle_izipay_ipn(request: Request):
    form = await request.form()
    answer = json.loads(form["kr-answer"])
    kr_hash = form["kr-hash"]

    if validate_kr_hash(json.dumps(answer), kr_hash):
        return {"response": answer.get("orderStatus")}
    return {"response": "Firma inválida"}, 400


def cleanup_pending_orders(db: Session, max_age_minutes: int = 60):
    cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
    db.query(Order).filter(
        Order.status == OrderStatus.PENDING,
        Order.created_at < cutoff,
    ).delete(synchronize_session=False)
    db.commit()