from datetime import datetime
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from ..core.database import Base
from .audit_mixin import AuditMixin
import enum

class User(Base, AuditMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)  # ← requerido, único
    full_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    company = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    failed_attempts = Column(Integer, default=0)
    lock_until = Column(DateTime, nullable=True)
    hashed_password = Column(String, nullable=False)

    items = relationship("Item", back_populates="owner")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    plan_assigned_at = Column(DateTime, nullable=True)

    plan = relationship("Plan")

class Item(Base, AuditMixin):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")


class Plan(Base, AuditMixin):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255), nullable=True)

    features = Column(JSON, nullable=True)
    is_free = Column(Boolean, default=False)
    validity_days = Column(Integer, nullable=True)


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"


class Order(Base, AuditMixin):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_reference = Column(String(100), nullable=True)

    # Relaciones
    user = relationship("User", back_populates="orders")
    plan = relationship("Plan")

class ConsentLog(Base):
    __tablename__ = "consent_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    policy_type = Column(String, nullable=False)  
    version = Column(String, nullable=False)
    accepted = Column(Boolean, nullable=False, default=True)   
    accepted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    description = Column(String, nullable=True)  

    user = relationship("User", backref="consent_logs")

class SecurityLog(Base, AuditMixin):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)   
    ip_address = Column(String(45), nullable=False)   
    event_type = Column(String(50), nullable=False)   
    description = Column(String(255), nullable=True)   

    user = relationship("User", backref="security_logs")