from operator import ge

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import company
from app.models.products import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductPatch, ProductUpdate
from app.security import get_current_user

product_router = APIRouter(
    prefix="/products", tags=["Products"], dependencies=[Depends(get_current_user)]
)


@product_router.get("/")  # LIST OD PRODUCTS
async def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = db.query(Product).filter_by(company_id=current_user.company_id).all()

    return products


@product_router.get("/{product_id}")  # CHOICE A PRODUCT
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = (
        db.query(Product)
        .filter_by(id=product_id, company_id=current_user.company_id)
        .first()
    )

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@product_router.post("/")  # CREATE ROUTE
async def create_product(
    product_create: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_product = Product(
        name=product_create.name,
        price=product_create.price,
        quantity=product_create.quantity,
        company_id=current_user.company_id,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {
        "message": "Product create successfully",
        "products": new_product,
    }


@product_router.delete("/{product_id}")  # DELETE PRODUCT
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(id=product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully", "id_product": product_id}


@product_router.put("/{product_id}")  # UPDATE PRODUCT
async def update_product(
    product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)
):
    product = db.query(Product).filter_by(id=product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = product_update.name
    product.price = product_update.price  # type: ignore
    product.quantity = product_update.quantity

    db.commit()
    db.refresh(product)

    return product


@product_router.patch("/{product_id}")  # PARTIAL UPDATE PRODUCT
async def partial_update_product(product_id: int, product_patch: ProductPatch):
    pass
