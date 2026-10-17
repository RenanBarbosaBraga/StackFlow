import datetime
import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:

    return password_hash.hash(password)


def verity_password(plain_password: str, hash_password: str) -> bool:

    return password_hash.verify(plain_password, hash_password)


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 0))  # noqa: PLW1508
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 0))  # noqa: PLW1508


def create_refresh_token(user_id: int) -> str:
    expire = datetime.datetime.now(datetime.UTC) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_MINUTES
    )

    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore


def create_access_token(user_id: int) -> str:

    expire = datetime.datetime.now(datetime.UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {"sub": str(user_id), "exp": expire}

    if SECRET_KEY is None or ALGORITHM is None:
        raise ValueError("SECRET_KEY and ALGORITHM must be configured")

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        user_id = int(payload.get("sub"))  # type: ignore

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid Token")

    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter_by(id=user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
