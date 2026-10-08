"""Generic audit log, written by SQLAlchemy hooks.

Every insert, update and delete on an audited table is recorded in `audit_log`
with who did it, when, which fields changed and a full snapshot of the row.
The log is only written for requests that bound an actor (see `bind_actor`),
so seeding and background jobs are not recorded.
"""

import contextlib
import datetime
import enum
import uuid
from contextvars import ContextVar
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable

from sqlalchemy import Date, DateTime, Enum, event, inspect, insert, select, text
from sqlalchemy.orm import Session

from server.db.base import Base
from server.exceptions import ResourceConflictError, ResourceNotFoundError
from server.models._mixins import utcnow
from server.models.audit_log import AuditLogModel

# Fields that are never written to the log, in snapshots or in changes.
REDACTED_FIELDS = {"password", "token", "secret", "api_key", "access_token"}
# Fields that change on every write and would only add noise.
IGNORED_CHANGE_FIELDS = {"updated_at"}


@dataclass(frozen=True)
class Actor:
    id: str | None
    username: str | None


_actor: ContextVar[Actor | None] = ContextVar("audit_actor", default=None)
_group: ContextVar[str | None] = ContextVar("audit_group", default=None)
_counter: ContextVar[list[int] | None] = ContextVar("audit_counter", default=None)
_action_hint: ContextVar[str | None] = ContextVar("audit_action_hint", default=None)
_reason: ContextVar[str | None] = ContextVar("audit_reason", default=None)


def bind_actor(actor: Actor, reason: str | None = None) -> str:
    """Start recording for the current request. Returns the group id."""
    group_id = str(uuid.uuid4())
    _actor.set(actor)
    _group.set(group_id)
    _counter.set([0])
    _reason.set(reason)
    _action_hint.set(None)
    return group_id


def unbind_actor() -> None:
    _actor.set(None)
    _group.set(None)
    _counter.set(None)
    _reason.set(None)
    _action_hint.set(None)


def current_group_id() -> str | None:
    return _group.get()


@contextlib.contextmanager
def audit_action(action: str):
    """Label the creates in this block, for example as a `restore`."""
    token = _action_hint.set(action)
    try:
        yield
    finally:
        _action_hint.reset(token)


# ---------------------------------------------------------------- what to audit


@dataclass(frozen=True)
class AuditSpec:
    # Returns (root_type, root_id) for the ADR this row belongs to, if any.
    root: Callable[[Any, Any], tuple[str, str] | None]


def _no_root(conn, obj):
    return None


def _adr_root(conn, obj):
    return ("adr", obj.id)


def _via_adr_id(conn, obj):
    return ("adr", obj.adr_id) if obj.adr_id else None


def _review_root(conn, obj):
    row = conn.execute(
        text("select adr_id from causality_assessment_level where id = :id"),
        {"id": obj.causality_assessment_level_id},
    ).first()
    return ("adr", row[0]) if row and row[0] else None


def audited_tables() -> dict[str, AuditSpec]:
    return {
        "adr": AuditSpec(_adr_root),
        "causality_assessment_level": AuditSpec(_via_adr_id),
        "review": AuditSpec(_review_root),
        "sms_message": AuditSpec(_via_adr_id),
        "medical_institution": AuditSpec(_no_root),
        "medical_institution_telephone": AuditSpec(_no_root),
    }


def _spec_for(obj) -> AuditSpec | None:
    table = getattr(obj, "__table__", None)
    if table is None:
        return None
    return audited_tables().get(table.name)


# ------------------------------------------------------------------ (de)serialise


def serialize_value(value: Any) -> Any:
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def _columns(obj) -> list[str]:
    return [attr.key for attr in inspect(obj).mapper.column_attrs]


def serialize_row(obj) -> dict[str, Any]:
    return {
        key: serialize_value(getattr(obj, key))
        for key in _columns(obj)
        if key not in REDACTED_FIELDS
    }


def deserialize_row(model_cls, data: dict[str, Any]) -> dict[str, Any]:
    """Turn a snapshot back into values a model can be built from."""
    values: dict[str, Any] = {}
    for column in model_cls.__table__.columns:
        if column.key not in data:
            continue
        value = data[column.key]
        if value is not None:
            if isinstance(column.type, Enum) and column.type.enum_class is not None:
                value = column.type.enum_class(value)
            elif isinstance(column.type, DateTime):
                value = datetime.datetime.fromisoformat(value)
            elif isinstance(column.type, Date):
                value = datetime.date.fromisoformat(value)
        values[column.key] = value
    return values


def _changes(obj) -> list[dict[str, Any]]:
    state = inspect(obj)
    changes = []
    for attr in state.mapper.column_attrs:
        key = attr.key
        if key in REDACTED_FIELDS or key in IGNORED_CHANGE_FIELDS:
            continue
        history = state.attrs[key].history
        if not history.has_changes():
            continue
        old = history.deleted[0] if history.deleted else None
        new = history.added[0] if history.added else getattr(obj, key)
        if serialize_value(old) != serialize_value(new):
            changes.append(
                {
                    "field": key,
                    "old": serialize_value(old),
                    "new": serialize_value(new),
                }
            )
    return changes


# ---------------------------------------------------------------------- writing


def _next_version(conn, entity_type: str, entity_id: str) -> int:
    current = conn.execute(
        select(text("max(version)"))
        .select_from(AuditLogModel.__table__)
        .where(
            AuditLogModel.__table__.c.entity_type == entity_type,
            AuditLogModel.__table__.c.entity_id == entity_id,
        )
    ).scalar()
    return (current or 0) + 1


def _entry(
    *, obj, spec, conn, actor, action, version, changes, snapshot, at=None
) -> dict[str, Any]:
    counter = _counter.get()
    seq = 0
    if counter is not None:
        counter[0] += 1
        seq = counter[0]
    root = spec.root(conn, obj)
    return {
        "id": str(uuid.uuid4()),
        "group_id": _group.get() or str(uuid.uuid4()),
        "seq": seq,
        "entity_type": obj.__table__.name,
        "entity_id": obj.id,
        "root_type": root[0] if root else None,
        "root_id": root[1] if root else None,
        "action": action,
        "version": version,
        "actor_id": actor.id if actor else None,
        "actor_username": actor.username if actor else None,
        "at": at or utcnow(),
        "changes": changes,
        "snapshot": snapshot,
        "reason": _reason.get(),
    }


def _baseline(obj, spec, conn, snapshot_before) -> dict[str, Any]:
    """Version 1 for a row that existed before auditing was switched on."""
    created = snapshot_before.get("created_at")
    at = datetime.datetime.fromisoformat(created) if created else None
    return _entry(
        obj=obj,
        spec=spec,
        conn=conn,
        actor=Actor(id=None, username="system (baseline)"),
        action="create",
        version=1,
        changes=None,
        snapshot=snapshot_before,
        at=at,
    )


def _record(session: Session, items: list[tuple[Any, str]]) -> None:
    """items: (object, "create" | "update" | "delete")"""
    actor = _actor.get()
    if actor is None or not items:
        return

    conn = session.connection()
    rows: list[dict[str, Any]] = []
    versions: dict[tuple[str, str], int] = {}

    for obj, action in items:
        spec = _spec_for(obj)
        key = (obj.__table__.name, obj.id)
        snapshot = serialize_row(obj)
        changes = None

        if action == "update":
            changes = _changes(obj)
            if not changes:
                continue
        elif action == "create":
            action = _action_hint.get() or "create"

        version = _next_version(conn, *key)

        if action in ("update", "delete") and version == 1:
            before = dict(snapshot)
            for change in changes or []:
                before[change["field"]] = change["old"]
            rows.append(_baseline(obj, spec, conn, before))
            version = 2

        versions[key] = version
        rows.append(
            _entry(
                obj=obj,
                spec=spec,
                conn=conn,
                actor=actor,
                action=action,
                version=version,
                changes=changes,
                snapshot=snapshot,
            )
        )

    if rows:
        conn.execute(insert(AuditLogModel.__table__), rows)


def _delete_order(items):
    """Children first, the order a cascading delete removes them in."""
    tables = {t.name: i for i, t in enumerate(AuditLogModel.metadata.sorted_tables)}
    return sorted(items, key=lambda item: tables.get(item.__table__.name, 0), reverse=True)


def _before_flush(session: Session, flush_context, instances) -> None:
    if _actor.get() is None:
        return
    deleted = _delete_order([o for o in session.deleted if _spec_for(o)])
    _record(session, [(o, "delete") for o in deleted])


def _after_flush(session: Session, flush_context) -> None:
    if _actor.get() is None:
        return
    items: list[tuple[Any, str]] = []
    created = [o for o in session.new if _spec_for(o)]
    tables = {t.name: i for i, t in enumerate(AuditLogModel.metadata.sorted_tables)}
    for obj in sorted(created, key=lambda o: tables.get(o.__table__.name, 0)):
        items.append((obj, "create"))
    for obj in session.dirty:
        if _spec_for(obj) and session.is_modified(obj, include_collections=False):
            items.append((obj, "update"))
    _record(session, items)


_registered = False


def register_audit_hooks() -> None:
    global _registered
    if _registered:
        return
    event.listen(Session, "before_flush", _before_flush)
    event.listen(Session, "after_flush", _after_flush)
    _registered = True


# ---------------------------------------------------------------------- restore


def model_for_table(table_name: str):
    for mapper in Base.registry.mappers:
        if mapper.local_table.name == table_name:
            return mapper.class_
    raise ValueError(f"No model for table {table_name}")


def restore_deleted(session: Session, entity_type: str, entity_id: str):
    """Undo the delete of one row, and everything that was deleted with it.

    A delete is logged as one group of rows (the row, its assessments, its
    reviews...). Recreate them all from their snapshots, and put back any
    field the same request changed on rows that still exist (for example an
    SMS message that was unlinked from the ADR). The caller commits.
    """
    last = (
        session.query(AuditLogModel)
        .filter_by(entity_type=entity_type, entity_id=entity_id, action="delete")
        .order_by(AuditLogModel.version.desc())
        .first()
    )
    if last is None:
        raise ResourceNotFoundError(f"No deleted {entity_type} with id {entity_id}")

    model_cls = model_for_table(entity_type)
    if session.get(model_cls, entity_id) is not None:
        raise ResourceConflictError(f"{entity_type} {entity_id} already exists")

    group = (
        session.query(AuditLogModel)
        .filter_by(group_id=last.group_id)
        .order_by(AuditLogModel.seq)
        .all()
    )
    table_order = {t.name: i for i, t in enumerate(Base.metadata.sorted_tables)}

    with audit_action("restore"):
        deleted = sorted(
            (r for r in group if r.action == "delete"),
            key=lambda r: table_order.get(r.entity_type, 0),
        )
        for row in deleted:
            cls = model_for_table(row.entity_type)
            session.add(cls(**deserialize_row(cls, row.snapshot)))
        session.flush()

        for row in (r for r in group if r.action == "update"):
            cls = model_for_table(row.entity_type)
            obj = session.get(cls, row.entity_id)
            if obj is None:
                continue
            for change in row.changes or []:
                old = deserialize_row(cls, {change["field"]: change["old"]})
                setattr(obj, change["field"], old[change["field"]])
        session.flush()

    return session.get(model_cls, entity_id)
