from typing import Optional

from requests import Session
from app.models.models import User
from app.core.database import SessionLocal

class UserService:
    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        db = SessionLocal()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()
            
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()