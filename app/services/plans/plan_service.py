from datetime import datetime, timedelta
from app.models.models import User, Plan
from app.core.database import SessionLocal

class PlanService:
    @staticmethod
    def get_plan_status(user: User) -> str:
        if not user or not user.plan_id or not user.plan_assigned_at:
            return "no_plan"

        db = SessionLocal()
        try:
            plan = db.query(Plan).filter(Plan.id == user.plan_id).first()
            if not plan:
                return "no_plan"

            expiration = user.plan_assigned_at + timedelta(days=plan.validity_days)
            return "active" if datetime.utcnow() <= expiration else "expired"
        finally:
            db.close()
