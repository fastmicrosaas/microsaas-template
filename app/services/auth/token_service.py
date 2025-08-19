from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import HTTPException, status
from app.core.config import get_settings
from app.utils.constants import REFRESH_TOKEN_TYPE, ACCESS_TOKEN_TYPE
settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


class TokenService:

    @staticmethod
    def _build_payload(data: dict, expires_delta: timedelta) -> dict:
        payload = data.copy()
        payload.update({"exp": datetime.utcnow() + expires_delta})
        return payload

    @staticmethod
    def _encode_token(payload: dict) -> str:
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_access_token(data: dict) -> str:
        expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = TokenService._build_payload(data, expires)
        return TokenService._encode_token(payload)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = TokenService._build_payload(data, expires)
        return TokenService._encode_token(payload)

    @staticmethod
    def decode_token(token: Optional[str]) -> Optional[dict]:
        if not token or not isinstance(token, str):
            return None
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            return None
        except JWTError:
            return None

    @staticmethod
    def decode_token_or_raise(token: str, token_type: str = ACCESS_TOKEN_TYPE) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{token_type.capitalize()} token expirado"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{token_type.capitalize()} token inválido"
            )

    @staticmethod
    def get_subject_from_token(token: Optional[str]) -> Optional[str]:
        payload = TokenService.decode_token(token)
        return payload.get("sub") if payload and "sub" in payload else None

    @staticmethod
    def verify_refresh_token(token: str) -> str:
        payload = TokenService.decode_token_or_raise(token, token_type=REFRESH_TOKEN_TYPE)
        subject = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=401, detail="Refresh token inválido")
        return subject

    @staticmethod
    def is_token_valid(token: Optional[str]) -> bool:
        return TokenService.decode_token(token) is not None

    @staticmethod
    def token_expiry_seconds() -> int:
        return ACCESS_TOKEN_EXPIRE_MINUTES * 60
