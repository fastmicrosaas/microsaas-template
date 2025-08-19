from sqlalchemy.orm import Session
from app.models.models import Plan
from app.core.database import SessionLocal
from app.core.config import get_settings

settings = get_settings()

def create_free_plan_if_not_exists():
    if not settings.HAS_FREE_DEMO:
        return  # 🔒 No crear plan si no está habilitado

    free_name = settings.FREE_PLAN_NAME
    if not free_name:
        return  # 🔒 No continuar si no hay nombre definido

    db: Session = SessionLocal()
    try:
        exists = db.query(Plan).filter(Plan.name == free_name).first()
        if not exists:
            db.add(Plan(
                name=free_name,
                price=0,
                description="Plan gratuito de prueba",
                is_free=True,
                validity_days=settings.FREE_PLAN_VALIDITY_DAYS,
                features={"max_projects": 3, "support": False}
            ))
            db.commit()
    finally:
        db.close()
