import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL não foi definida")

test_engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture
def db_connection():
    Base.metadata.create_all(bind=test_engine)

    connection = test_engine.connect()
    transaction = connection.begin()

    try:
        yield connection
    finally:
        if transaction.is_active:
            transaction.rollback()

        connection.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(db_connection):
    TestingSessionLocal = sessionmaker(
        bind=db_connection,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_connection):
    TestingSessionLocal = sessionmaker(
        bind=db_connection,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    )

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
