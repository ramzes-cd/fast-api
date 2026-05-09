from datetime import datetime, timedelta, timezone
from jose import jwt

from src.core.config import settings


class JWTService:
    
    @staticmethod
    def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:

        to_encode = {
            "sub": str(user_id)
        }

        if expires_delta:
            expire = (datetime.now(timezone.utc) + expires_delta)
        else:
            expire = (datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

        to_encode.update({
            "exp": expire
        })

        encoded_jwt = jwt.encode(
            claims=to_encode,
            key=settings.SECRET_AUTH_KEY.get_secret_value(),
            algorithm=settings.AUTH_ALGORITHM,
        )

        return encoded_jwt
