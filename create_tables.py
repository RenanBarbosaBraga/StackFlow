from app.database.connection import Base, engine
from app.models.company import Company
from app.models.products import Product
from app.models.refresh_token import RefreshToken
from app.models.user import User

Base.metadata.create_all(bind=engine)

print("colunas criadas com sucesso")
