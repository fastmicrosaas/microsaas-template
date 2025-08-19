from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import Extra
import os

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int 
    DATABASE_URL: str = "sqlite:///./test.db"
    ENVIRONMENT: str = "development"

    #SMTP config
    SMTP_PROVIDER: str = ""
    RECIEVER_EMAIL: str = ""

    # Credenciales para Gmail
    SMTP_HOST_GMAIL: str = "smtp.gmail.com"
    SMTP_PORT_GMAIL: int = 465
    SMTP_USER_GMAIL: str = ""
    SMTP_PASS_GMAIL: str = ""

    # Credenciales para Hostinger/Titan
    SMTP_HOST_HOSTINGER: str = ""
    SMTP_PORT_HOSTINGER: int = 465
    SMTP_USER_HOSTINGER: str = ""
    SMTP_PASS_HOSTINGER: str = ""

    #payments
    PAYMENT_GATEWAY: str = ""
    IZIPAY_ENV: str = "TEST"
    IZIPAY_IPN_URL: str = ""
    IZIPAY_ENDPOINT: str = ""
    IZIPAY_USERNAME: str = ""
    IZIPAY_PASSWORD: str = ""
    IZIPAY_PUBLIC_KEY: str = ""
    IZIPAY_HMACSHA256: str = ""

    HAS_FREE_DEMO: bool = False
    FREE_PLAN_NAME: str = ""
    FREE_PLAN_VALIDITY_DAYS: int = 1

    RECAPTCHA_SECRET_KEY: str = ""
    RECAPTCHA_SITE_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = Extra.allow
        
@lru_cache
def get_settings():
    return Settings()

 