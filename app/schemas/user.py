from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class RefreshTokenSchema(BaseModel):
    refresh_token: str

    class Config:
        from_attributes = True
