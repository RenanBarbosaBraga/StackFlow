from pydantic import BaseModel, EmailStr


class InvitationCreate(BaseModel):
    email: EmailStr

    class Config:
        from_attributes = True
