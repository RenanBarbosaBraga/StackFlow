from pydantic import BaseModel, EmailStr, Field


class InvitationCreate(BaseModel):
    email: EmailStr

    class Config:
        from_attributes = True


class InvitationAccept(BaseModel):
    token: str
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8)

    class Config:
        from_attributes = True
