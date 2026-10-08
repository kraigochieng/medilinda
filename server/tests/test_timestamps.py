import time

from server.models.user import UserModel


def make_user(db, id):
    user = UserModel(id=id, username=id, password=f"pw-{id}")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_created_at_is_set_when_each_row_is_written(db):
    first = make_user(db, "first")
    time.sleep(0.01)
    second = make_user(db, "second")

    assert second.created_at > first.created_at


def test_updated_at_moves_when_a_row_changes(db):
    user = make_user(db, "u1")
    before = user.updated_at
    time.sleep(0.01)

    user.first_name = "Changed"
    db.commit()
    db.refresh(user)

    assert user.updated_at > before
    assert user.created_at < user.updated_at
