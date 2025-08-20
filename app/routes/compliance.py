from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from requests import Session
from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.models.models import ConsentLog, User
from app.utils.constants import MARKETING_DESCRIPTION
from app.core.presentation.templates import render_template
import datetime   
from app.core.security import limiter 
from pathlib import Path
import json
from fastapi import status

BASE_DIR = Path(__file__).resolve().parent.parent

def load_legal_info():
    data_path = BASE_DIR / "data" / "legal.json"
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)

router = APIRouter(tags=["Legal"])
 
@router.get("/privacy", response_class=HTMLResponse)
@limiter.limit("100/minute")
def privacy_page(request: Request):
    legal = load_legal_info()
    return render_template(
        request,
        "home/privacy/index.html",
        {
            "datetime": datetime.datetime.utcnow(),
            **legal
        }
    )

@router.get("/terms", response_class=HTMLResponse)
@limiter.limit("100/minute")
def terms_page(request: Request):
    legal = load_legal_info()
    return render_template(
        request,
        "home/terms/index.html",
        {
            "datetime": datetime.datetime.utcnow(),
             **legal
        }
    )

@router.get("/cookies", response_class=HTMLResponse)
@limiter.limit("100/minute")
def cookies_page(request: Request):
    return render_template(
        request,
        "home/cookies/index.html",
        {
            "datetime": datetime.datetime.utcnow()
        }
    )

@router.post("/consents", status_code=201)
def save_consent(
    request: Request,
    policy_type: str = Form(...),  # "privacy", "cookies", "terms"
    version: str = Form(...),
    accepted: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if policy_type not in {"privacy", "cookies", "terms", "dpa_terms", "marketing"}:
        raise HTTPException(status_code=400, detail="Tipo de política inválido")
    
    if not current_user:
         return Response(status_code=status.HTTP_204_NO_CONTENT)

    consent = ConsentLog(
        user_id=current_user.id if current_user else None,
        policy_type=policy_type,
        version=version,
        description=MARKETING_DESCRIPTION.strip(),
        accepted=accepted,
        accepted_at=datetime.datetime.utcnow(),
        ip_address=request.client.host
    )
    db.add(consent)
    db.commit()

    return {"message": "Consentimiento registrado correctamente"}

@router.get("/data-processing-agreement")
async def view_dpa_page(request: Request):
    dpa_status = [
        {"provider": "Mailgun", "status": "si", "notes": "Requiere firmar manualmente desde su sitio web"},
    ]
    return render_template(
        request,
        "home/dpa/index.html",
        {"dpa_status": dpa_status}
        )