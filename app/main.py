from fastapi import FastAPI

from app.routes.auth import auth_router
from app.routes.invitations import invitation_router
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
app.include_router(auth_router)
app.include_router(invitation_router)
