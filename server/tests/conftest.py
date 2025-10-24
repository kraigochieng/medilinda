from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from server.db.base import Base
from server.dependencies import get_db
from server.main import app
from server.services.auth import get_current_active_user

from tests.db import TestSessionLocal, test_engine
from tests.dependencies import override_get_current_active_user


@asynccontextmanager
async def no_lifespan(app):
    yield


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    # Clear lifespan
    app.router.lifespan_context = no_lifespan

    # Add pagination
    add_pagination(app)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
