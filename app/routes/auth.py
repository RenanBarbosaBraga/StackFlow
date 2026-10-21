import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.company import Company
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import (
    RefreshTokenSchema,
    UserCreate,
    UserLogin,
)
from app.security import (
    create_access_token,
    generate_refresh_token,
    get_current_user,
    hash_password,
    hash_refresh_token,
    save_refresh_token,
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
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter_by(email=user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    company_name = " ".join(user_data.company_name.split())

    existing_company = (
        db.query(Company).filter(Company.name.ilike(company_name)).first()
    )

    if existing_company:
        raise HTTPException(
            status_code=409,
            detail="Company already exists. Ask an administrator for an invitation.",
        )

    try:
        company = Company(name=company_name)
        db.add(company)
        db.flush()

        new_user = User(
            name=user_data.name.strip(),
            email=user_data.email,
            company_id=company.id,
            hashed_password=hash_password(user_data.password),
            is_admin=True,
        )

        db.add(new_user)
        db.commit()
        db.refresh(company)
        db.refresh(new_user)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "User and company registered successfully",
        "company": {
            "id": company.id,
            "name": company.name,
        },
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
        },
    }


@auth_router.post("/login")
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter_by(email=user_data.email).first()

    if not user or not verity_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(user.id)

    refresh_token = generate_refresh_token()
    save_refresh_token(user.id, refresh_token, db)
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_router.post("/refresh")
def refresh_access_token(
    data: RefreshTokenSchema,
    db: Session = Depends(get_db),
):
    old_token_hash = hash_refresh_token(data.refresh_token)

    try:
        stored_token = (
            db.query(RefreshToken)
            .filter_by(token_hash=old_token_hash)
            .with_for_update()
            .first()
        )

        if stored_token is None or stored_token.revoked:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired refresh token",
            )

        if stored_token.expired_at <= datetime.datetime.now(datetime.UTC):
            raise HTTPException(
                status_code=401,
                detail="Expired refresh token",
            )

        user_id = stored_token.user_id

        stored_token.revoked = True

        new_refresh_token = generate_refresh_token()

        new_access_token = create_access_token(user_id)

        save_refresh_token(user_id, new_refresh_token, db)
        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
