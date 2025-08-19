from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Item
from app.core.security import ownership_dependency
from app.core.presentation.templates import templates
from app.core.security import get_current_user
from app.models.models import User
from app.core.presentation.templates import render_template

router = APIRouter(tags=["Item"])

@router.post("/items", response_class=HTMLResponse)
async def dashboard_add_item(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.add(Item(name=name, owner_id=current_user.id))
    db.commit()

    items = db.query(Item).filter(Item.owner_id == current_user.id).all()

    return render_template(
        request,
        "dashboard/components/items_list.html",
        {"items": items},
        with_csrf=True
    )

@router.delete("/items/delete/{item_id}", response_class=HTMLResponse)
async def dashboard_delete_item(
    request: Request,
    item: Item = Depends(ownership_dependency(Item, "item_id")),
    db: Session = Depends(get_db)
):
    db.delete(item)
    db.commit()

    items = db.query(Item).filter(Item.owner_id == item.owner_id).all()

    return render_template(
        request,
        "dashboard/components/items_list.html",
        {"items": items},
        with_csrf=True
    )
