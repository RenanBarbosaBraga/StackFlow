from sqlalchemy import text

from app.database.connection import engine

with engine.connect() as connection:
    try:
        result = connection.execute(text("SELECT 1"))
        print("Conexão funcionando!", result.scalar())
    except Exception as error:
        print("Erro ao se conetar.", error)
