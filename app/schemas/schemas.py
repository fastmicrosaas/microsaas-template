from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional
from decimal import Decimal
from enum import Enum


# -------------------
# ITEMS
# -------------------
class ItemCreate(BaseModel):
    name: str


class ItemOut(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# -------------------
# USERS
# -------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    company: Optional[str]
    job_title: Optional[str]

    class Config:
        orm_mode = True


# -------------------
# PLANS
# -------------------
class PlanBase(BaseModel):
    name: str
    price: Decimal
    description: Optional[str] = None


class PlanCreate(PlanBase):
    pass


class PlanOut(PlanBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# -------------------
# ORDERS
# -------------------
class OrderStatusEnum(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"


class OrderCreate(BaseModel):
    plan_id: int


class OrderOut(BaseModel):
    id: int
    plan_id: int
    status: OrderStatusEnum
    payment_reference: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
