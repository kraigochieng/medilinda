import datetime
import uuid

from sqlalchemy import Column, DateTime, String


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class TimestampMixin:
    # Pass the function, not its result: a value would be computed once at
    # import time and every row would get the server start time.
    created_at = Column(DateTime, default=utcnow)  # Set at creation
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)  # Set on change


class IDMixin:
    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
