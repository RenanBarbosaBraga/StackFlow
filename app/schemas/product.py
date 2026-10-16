from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    name: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)

    class Config:
        from_attributes = True


class ProductPatch(BaseModel):
    name: str | None = None
    price: float | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)

    class Config:
        from_attributes = True
