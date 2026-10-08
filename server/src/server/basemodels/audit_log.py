from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


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
    snapshot: dict[str, Any] | None = None
