from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import RefreshTokenSchema, UserCreate, UserLogin
from app.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verity_password,
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.get("/")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return users


@auth_router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }


@auth_router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User found successfully", "user": user}


@auth_router.post("/register", status_code=201)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter_by(email=user_data.email).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exist")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email},
    }


@auth_router.post("/login")
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter_by(email=user_data.email).first()

    if not user or not verity_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_router.post("/refresh")
async def refresh_access_token(data: RefreshTokenSchema):
    refresh_token = data.refresh_token

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=ALGORITHM)

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token(user_id)

    return {"access_token": new_access_token, "token_type": "bearer"}
