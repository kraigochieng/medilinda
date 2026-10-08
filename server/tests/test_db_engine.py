from server.db import engine as engine_module


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
    assert kwargs["pool_pre_ping"] is True


def test_accepts_https_and_bare_host_urls(monkeypatch):
    fake = FakeCreateEngine()
    monkeypatch.setattr(engine_module, "create_engine", fake)

    for value in ["https://db.turso.io", "db.turso.io", "libsql://db.turso.io/"]:
        engine_module.build_engine(value, "t")

    assert {url for url, _ in fake.calls} == {"sqlite+libsql://db.turso.io?secure=true"}


def test_module_engine_is_local_sqlite_when_turso_is_not_configured():
    assert engine_module.engine.url.drivername == "sqlite"
