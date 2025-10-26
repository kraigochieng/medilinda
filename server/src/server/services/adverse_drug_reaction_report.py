from fastapi_pagination import Page
from sqlalchemy.orm import Session

from server.basemodels.adverse_drug_reaction_report import ADRGetResponse
from server.repositories.adverse_drug_reaction_report import (
    AdverseDrugReactionReportRepository,
)


class AdverseDrugReactionReportService:
    def __init__(self, db: Session):
        self.repository = AdverseDrugReactionReportRepository(db)

    def get(self, query: str | None) -> Page[ADRGetResponse]:
        return self.repository.get(query=query)

    def get_by_id(self, id: str) -> ADRGetResponse | None:
        return self.repository.get_by_id(id)

    def delete_by_id(self, id: str) -> bool:
        return self.repository.delete(id)
