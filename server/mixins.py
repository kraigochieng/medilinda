import datetime
import uuid

from sqlalchemy import Column, DateTime, String


class TimestampMixin:
    created_at = Column(
        DateTime, default=datetime.datetime.now(datetime.timezone.utc)
    )  # Set at creation
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))


class IDMixin:
    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
