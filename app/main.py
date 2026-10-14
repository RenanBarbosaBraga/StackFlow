from fastapi import FastAPI

from app.routes.products import product_router

app = FastAPI(
    title="StackFlow API",
    description="API para gerenciamento de estoque",
    version="0.1.0",
)


@app.get("/")
def inicio():
    return {"mensagem": "StackFlow API funcionando"}


app.include_router(product_router)
