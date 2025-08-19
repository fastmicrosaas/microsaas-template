from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.core.presentation.templates import render_template
from datetime import datetime
from app.core.security import limiter 
import os

router = APIRouter(tags=["Landing Page"])

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
 
@router.get("/", response_class=HTMLResponse)
@limiter.limit("100/minute")
def landing_saas(request: Request):
    return render_template(request, "home/index.html", {"year": datetime.now().year})

