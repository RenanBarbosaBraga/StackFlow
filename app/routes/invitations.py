import datetime
import hashlib
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.invitation import Invitation
from app.models.user import User
from app.schemas.invitation import InvitationCreate
from app.security import (
    generate_invitation_token,
    get_current_admin,
    hash_invitation_token,
)

invitation_router = APIRouter(
    prefix="/invitation", tags=["Invitation"], dependencies=[Depends(get_current_admin)]
)


@invitation_router.post("/")
async def create_invitation(
    invitation_data: InvitationCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter_by(email=invitation_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    now = datetime.datetime.now(datetime.UTC)

    existing_invitation = (
        db.query(Invitation)
        .filter(
            Invitation.company_id == current_user.company_id,
            Invitation.email == invitation_data.email,
            Invitation.accepted_at.is_(None),
            Invitation.expires_at > now,
        )
        .first()
    )

    if existing_invitation:
        raise HTTPException(
            status_code=409,
            detail="An active invitation already exists",
        )

    token = generate_invitation_token()
    token_hash = hash_invitation_token(token)

    expires_at = datetime.datetime.now(datetime.UTC) + timedelta(hours=24)

    new_invitation = Invitation(
        company_id=current_user.company_id,
        email=invitation_data.email,
        token_hash=token_hash,
        expires_at=expires_at,
        created_by=current_user.id,
    )

    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)

    return {
        "message": "Invitation created successfully",
        "email": new_invitation.email,
        "company_id": new_invitation.company_id,
        "expires_at": new_invitation.expires_at,
        "invitation_token": token,
    }
