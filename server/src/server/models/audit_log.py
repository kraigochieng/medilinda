import uuid

from sqlalchemy import JSON, Column, DateTime, Index, Integer, String, UniqueConstraint

from ..db.base import Base
from ._mixins import utcnow


class AuditLogModel(Base):
    """Append-only record of every change to an audited table.

    Rows are only ever inserted. `snapshot` holds the full row as it was after
    the change (or just before it, for a delete), so any version can be rebuilt.
    """

    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Every row written by one request shares a group id. `seq` keeps their order.
    group_id = Column(String, nullable=False)
    seq = Column(Integer, nullable=False, default=0)

    entity_type = Column(String, nullable=False)  # table name, e.g. "adr"
    entity_id = Column(String, nullable=False)
    # The ADR an entity belongs to, so one ADR can show a single timeline.
    root_type = Column(String, nullable=True)
    root_id = Column(String, nullable=True)

    action = Column(String, nullable=False)  # create | update | delete | restore
    version = Column(Integer, nullable=False)  # 1, 2, 3... per entity

    # Username is copied so history stays readable if an account changes.
    actor_id = Column(String, nullable=True)
    actor_username = Column(String, nullable=True)
    at = Column(DateTime, nullable=False, default=utcnow)

    changes = Column(JSON, nullable=True)  # [{"field", "old", "new"}]
    snapshot = Column(JSON, nullable=True)
    reason = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", "version", name="uq_audit_version"),
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_root", "root_type", "root_id"),
        Index("ix_audit_group", "group_id"),
        Index("ix_audit_at", "at"),
    )
