from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page, Params
from sqlalchemy.orm import Session

from server.basemodels.audit_log import AuditLogGetResponse
from server.dependencies import get_db
from server.repositories.audit_log import AuditLogRepository

router = APIRouter(prefix="/api/v1/audit-logs", tags=["audit", "v1"])


def get_audit_log_repository(db: Session = Depends(get_db)):
    return AuditLogRepository(db)


@router.get(
    "/",
    response_model=Page[AuditLogGetResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def get_audit_logs(
    pagination_params: Params = Depends(),
    entity_type: str | None = Query(None, description="Table name, e.g. adr"),
    entity_id: str | None = None,
    root_id: str | None = Query(None, description="ADR the change belongs to"),
    actor_id: str | None = None,
    action: str | None = Query(None, description="create, update, delete or restore"),
    include_snapshot: bool = Query(False, description="Include the full row"),
    repository: AuditLogRepository = Depends(get_audit_log_repository),
):
    page = repository.get(
        pagination_params=pagination_params,
        entity_type=entity_type,
        entity_id=entity_id,
        root_id=root_id,
        actor_id=actor_id,
        action=action,
    )

    if not include_snapshot:
        page.items = [
            AuditLogGetResponse.model_validate(row).model_copy(update={"snapshot": None})
            for row in page.items
        ]

    return page
