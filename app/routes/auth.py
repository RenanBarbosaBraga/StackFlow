from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.security import create_access_token, hash_password, verity_password

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.get("/")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return users


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

    token = create_access_token(user.id)

    return {"access_token": token, "token_type": "bearer"}
