from sqlalchemy import Engine, create_engine

from server.settings import settings

from . import DB_PATH


def build_engine(
    turso_url: str | None = None,
    turso_token: str | None = None,
    sqlite_path=DB_PATH,
) -> Engine:
    """Use Turso when a database URL is set, otherwise the local SQLite file.

    The local file keeps development and the tests simple. Turso keeps data
    across restarts on hosts without a persistent disk (e.g. Render).
    """
    if not turso_url:
        return create_engine(f"sqlite:///{sqlite_path}")

    # Accept libsql://host, https://host or a bare host.
    host = turso_url.split("://", 1)[-1].rstrip("/")

    return create_engine(
        f"sqlite+libsql://{host}?secure=true",
        connect_args={"auth_token": turso_token},
        pool_pre_ping=True,
        pool_recycle=300,
    )


engine = build_engine(
    settings.turso_app_database_url,
    settings.turso_app_auth_token,
)
