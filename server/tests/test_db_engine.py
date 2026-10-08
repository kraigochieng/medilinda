import sqlite3

import pytest
from server.db import engine as engine_module
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool, QueuePool


class FakeCreateEngine:
    def __init__(self):
        self.calls = []

    def __call__(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return object()


def test_uses_local_sqlite_without_a_turso_url(monkeypatch, tmp_path):
    fake = FakeCreateEngine()
    monkeypatch.setattr(engine_module, "create_engine", fake)

    engine_module.build_engine(None, None, sqlite_path=tmp_path / "db.sqlite")

    assert fake.calls == [(f"sqlite:///{tmp_path / 'db.sqlite'}", {})]


def test_empty_turso_url_falls_back_to_sqlite(monkeypatch, tmp_path):
    fake = FakeCreateEngine()
    monkeypatch.setattr(engine_module, "create_engine", fake)

    engine_module.build_engine("", "token", sqlite_path=tmp_path / "db.sqlite")

    assert fake.calls[0][0].startswith("sqlite:///")


def test_connects_to_turso_with_the_auth_token(monkeypatch):
    fake = FakeCreateEngine()
    monkeypatch.setattr(engine_module, "create_engine", fake)

    engine_module.build_engine("libsql://medilinda-app-me.turso.io", "secret-token")

    url, kwargs = fake.calls[0]
    assert url == "sqlite+libsql://medilinda-app-me.turso.io?secure=true"
    assert kwargs["connect_args"] == {"auth_token": "secret-token"}
    # Turso closes the stream of an idle connection, so none is kept between requests.
    assert kwargs["poolclass"] is NullPool
    assert "pool_pre_ping" not in kwargs


def test_accepts_https_and_bare_host_urls(monkeypatch):
    fake = FakeCreateEngine()
    monkeypatch.setattr(engine_module, "create_engine", fake)

    for value in ["https://db.turso.io", "db.turso.io", "libsql://db.turso.io/"]:
        engine_module.build_engine(value, "t")

    assert {url for url, _ in fake.calls} == {"sqlite+libsql://db.turso.io?secure=true"}


def test_module_engine_is_local_sqlite_when_turso_is_not_configured():
    assert engine_module.engine.url.drivername == "sqlite"


# --- A connection that went stale while the server was idle -----------------------------
#
# Turso closes the stream of an idle connection. The next query on it fails with a plain
# ValueError ("Hrana: ... stream not found"), which SQLAlchemy does not see as a lost
# connection. The fake below fails the same way once it is marked stale.


class StaleCursor(sqlite3.Cursor):
    def execute(self, *args, **kwargs):
        if self.connection.stale:
            raise ValueError('Hrana: `api error: `status=404 Not Found, body={"error":"stream not found"}``')
        return super().execute(*args, **kwargs)


class StaleConnection(sqlite3.Connection):
    stale = False

    def cursor(self, factory=StaleCursor):
        return super().cursor(factory)


@pytest.fixture
def connections(tmp_path):
    made = []

    def make():
        connection = sqlite3.connect(
            tmp_path / "stale.db", factory=StaleConnection, check_same_thread=False
        )
        made.append(connection)
        return connection

    def go_idle():
        """The server sat idle: every open connection is now stale."""
        for connection in made:
            connection.stale = True

    return make, go_idle


def ask(engine):
    with engine.connect() as connection:
        return connection.execute(text("select 1")).scalar()


def test_the_old_pool_settings_break_after_an_idle_period(connections):
    make, go_idle = connections
    engine = create_engine(
        "sqlite://", creator=make, poolclass=QueuePool, pool_pre_ping=True, pool_recycle=300
    )

    assert ask(engine) == 1
    go_idle()

    with pytest.raises(ValueError, match="stream not found"):
        ask(engine)


def test_a_fresh_connection_for_each_request_survives_an_idle_period(connections):
    make, go_idle = connections
    engine = create_engine("sqlite://", creator=make, poolclass=NullPool)

    assert ask(engine) == 1
    go_idle()

    assert ask(engine) == 1
    assert ask(engine) == 1
