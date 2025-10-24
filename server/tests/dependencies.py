from server.basemodels.user import UserDetailsBaseModel

from tests.db import TestSessionLocal


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def override_get_current_active_user():
    return UserDetailsBaseModel(
        id="1",
        username="testuser",
        first_name="Test",
        last_name="User",
        disabled=False,
    )
