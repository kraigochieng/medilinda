from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from server.utils.audit_summary import summarize


class AuditChange(BaseModel):
    field: str
    old: Any = None
    new: Any = None


class AuditLogGetResponse(BaseModel):
    """One audited change. `snapshot` is the full row after the change (or just
    before it, for a delete). It is left out of long lists to keep them small."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    group_id: str
    entity_type: str
    entity_id: str
    root_type: str | None = None
    root_id: str | None = None
    action: str
    version: int
    actor_id: str | None = None
    actor_username: str | None = None
    at: datetime
    changes: list[AuditChange] | None = None
    reason: str | None = None
    # A few fields that say what the entry is about, even when the snapshot is left out.
    summary: dict[str, Any] | None = None
    snapshot: dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def _add_summary(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data

        values = {
            name: getattr(data, name, None)
            for name in cls.model_fields
            if name != "summary"
        }
        values["summary"] = summarize(data.entity_type, data.snapshot)
        return values
