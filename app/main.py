from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import auth_router
from app.routes.invitations import invitation_router
from app.routes.products import product_router
from app.routes.public_invitation import public_invitation_router

app = FastAPI(
    title="StackFlow API",
    description="API para gerenciamento de estoque",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def inicio():
    return {"mensagem": "StackFlow API funcionando"}


app.include_router(product_router)
app.include_router(auth_router)
app.include_router(invitation_router)
app.include_router(public_invitation_router)
