from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from server.exceptions import ResourceNotFoundError
from server.models.audit_log import AuditLogModel


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(
        self,
        pagination_params: Params,
        entity_type: str | None = None,
        entity_id: str | None = None,
        root_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
    ) -> Page[AuditLogModel]:
        stmt = select(AuditLogModel)

        filters = {
            AuditLogModel.entity_type: entity_type,
            AuditLogModel.entity_id: entity_id,
            AuditLogModel.root_id: root_id,
            AuditLogModel.actor_id: actor_id,
            AuditLogModel.action: action,
        }
        for column, value in filters.items():
            if value:
                stmt = stmt.where(column == value)

        stmt = stmt.order_by(desc(AuditLogModel.at), desc(AuditLogModel.seq))

        return paginate(self.db, stmt, params=pagination_params)

    def versions_of(self, entity_type: str, entity_id: str) -> list[AuditLogModel]:
        stmt = (
            select(AuditLogModel)
            .where(
                AuditLogModel.entity_type == entity_type,
                AuditLogModel.entity_id == entity_id,
            )
            .order_by(desc(AuditLogModel.version))
        )
        return list(self.db.scalars(stmt))

    def get_version(
        self, entity_type: str, entity_id: str, version: int
    ) -> AuditLogModel:
        stmt = select(AuditLogModel).where(
            AuditLogModel.entity_type == entity_type,
            AuditLogModel.entity_id == entity_id,
            AuditLogModel.version == version,
        )
        row = self.db.scalar(stmt)

        if row is None:
            raise ResourceNotFoundError(
                f"{entity_type} {entity_id} has no version {version}"
            )

        return row
