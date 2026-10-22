import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.invitation import Invitation
from app.models.user import User
from app.schemas.invitation import InvitationAccept
from app.security import get_current_user, hash_invitation_token, hash_password

public_invitation_router = APIRouter(
    prefix="/public_invitation", tags=["Public Invitation"]
)


@public_invitation_router.post("/accept")
async def accept_invitation(
    invitation_data: InvitationAccept, db: Session = Depends(get_db)
):
    token_hash = hash_invitation_token(invitation_data.token)

    invitation = db.query(Invitation).filter_by(token_hash=token_hash).first()

    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")

    if invitation.accepted_at is not None:
        raise HTTPException(status_code=409, detail="Invitation already accepted")

    now = datetime.datetime.now(datetime.UTC)

    if invitation.expires_at <= now:
        raise HTTPException(status_code=410, detail="Expired invitation")

    if invitation_data.email.strip().lower() != invitation.email.strip().lower():
        raise HTTPException(
            status_code=403, detail="This invitation belongs to another email"
        )
    try:
        new_user = User(
            name=invitation_data.name.strip(),
            email=invitation.email,
            company_id=invitation.company_id,
            hashed_password=hash_password(invitation_data.password),
            is_admin=False,
        )

        db.add(new_user)

        invitation.accepted_at = now

        db.commit()
        db.refresh(new_user)
        db.refresh(invitation)
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Invitation accepted successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "company_id": new_user.company_id,
        },
    }
