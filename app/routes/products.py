from multiprocessing import process

from fastapi import APIRouter, HTTPException

from app.schemas import ProductCreate, ProductPatch, ProductUpdate

product_router = APIRouter(prefix="/products", tags=["Products"])

products = [
    {"id": 1, "name": "Páprica Doce 20g", "price": 2.50, "quantity": 3000},
    {"id": 2, "name": "Páprica Defumada 20g", "price": 2.60, "quantity": 3000},
]


@product_router.get("/")  # LIST OD PRODUCTS
async def get_products():
    return {"message": "List of products", "products": products}


@product_router.get("/{product_id}")  # CHOICE A PRODUCT
async def get_product(product_id: int):
    product = next(
        (product for product in products if product["id"] == product_id), None
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product_id": product_id, "product": product}


@product_router.post("/")  # CREATE ROUTE
async def create_product(product_create: ProductCreate):
    product = product_create.model_dump()
    product["id"] = max((product["id"] for product in products), default=0) + 1
    products.append(product)
    return {"message": "Product create successfully", "product": product}


@product_router.delete("/{product_id}")  # DELETE PRODUCT
async def delete_product(product_id: int):
    product = next((item for item in products if item["id"] == product_id), None)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    products.remove(product)

    return {"message": "Product deleted successfully", "id_product": product_id}


@product_router.put("/{product_id}")
async def update_product(product_id: int, product_update: ProductUpdate):
    product = next((item for item in products if item["id"] == product_id), None)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product["name"] = product_update.name
    product["price"] = product_update.price
    product["quantity"] = product_update.quantity

    return {"message": "Product update successfully", "product": product}


@product_router.patch("/{product_id}")
async def partial_update_product(product_id: int, product_patch: ProductPatch):
    product = next((item for item in products if item["id"] == product_id), None)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    changes = product_patch.model_dump(exclude_unset=True)

    for field, value in changes.items():
        if value is None:
            raise HTTPException(status_code=422, detail=f"{field} cannot be null")

        product[field] = value

    return {"message": "Product partially updated successfully", "product": product}
