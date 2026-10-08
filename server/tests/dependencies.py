from server.basemodels.user import UserDetailsBaseModel
from server.utils.audit import Actor, bind_actor

from tests.db import TestSessionLocal


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def override_get_current_active_user():
    # Like the real dependency, tell the audit log who is making the request.
    bind_actor(Actor(id="1", username="testuser"))

    return UserDetailsBaseModel(
        id="1",
        username="testuser",
        first_name="Test",
        last_name="User",
        disabled=False,
    )
