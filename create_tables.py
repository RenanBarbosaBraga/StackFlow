from app.database.connection import Base, engine
from app.models.products import Product
from app.models.user import User

Base.metadata.create_all(bind=engine)

print("colunas criadas com sucesso")
