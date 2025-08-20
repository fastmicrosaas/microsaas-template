# routers/settings.py

from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.core.presentation.templates import render_template, templates
from starlette.status import HTTP_200_OK

router = APIRouter(prefix="/dashboard/settings", tags=["Settings"])
 
@router.get("/profile")
def view_profile(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return render_template(
        request,
        "dashboard/profile/index.html",
        {
            "user": current_user,
            "edit_mode": False
        }
    )

@router.get("/profile/edit")
def edit_profile_form(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return render_template(
        request,
        "dashboard/profile/index.html",
        {
            "user": current_user,
            "edit_mode": True
        },
        with_csrf=True
    )

@router.patch("/profile/edit")
def update_profile_htmx(
    request: Request,
    full_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(...),
    company: str = Form(...),
    job_title: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.full_name = full_name
    current_user.last_name = last_name
    current_user.phone_number = phone_number
    current_user.company = company
    current_user.job_title = job_title
    db.commit()

    response = Response(status_code=204)
    response.headers["HX-Redirect"] = "/dashboard/profile"
    return response

@router.delete("/profile/delete")
def delete_account(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.delete(current_user)
    db.commit()

    response = Response(status_code=204)
    response.headers["HX-Redirect"] = "/auth/logout"
    return response

@router.get("/export")
async def export_user_data(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "last_name": current_user.last_name,
        "phone_number": current_user.phone_number,
        "company": current_user.company,
        "job_title": current_user.job_title,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }

    return JSONResponse(
        content=user_data,
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{current_user.id}.json"
        }
    )
