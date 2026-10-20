from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=150)
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class RefreshTokenSchema(BaseModel):
    refresh_token: str

    class Config:
        from_attributes = True


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
