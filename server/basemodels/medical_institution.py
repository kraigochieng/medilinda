from typing import List

from pydantic import BaseModel


# Medical Institution
class MedicalInstitutionGetResponse(BaseModel):
    id: str
    name: str
    mfl_code: str | None = None
    dhis_code: str | None = None
    county: str | None = None
    sub_county: str | None = None


class MedicalInstitutionPostRequest(BaseModel):
    name: str
    mfl_code: str | None = None
    dhis_code: str | None = None
    county: str | None = None
    sub_county: str | None = None


# Medical Institution Telephone
class MedicalInstitutionTelephoneGetResponse(BaseModel):
    medical_institution_id: str
    telephone: str


class MedicalInstitutionTelephonePostRequest(BaseModel):
    medical_institution_id: str
    telephone: str


class MultipleMedicalInstitutionTelephonePostRequest(BaseModel):
    telephones: List[MedicalInstitutionTelephonePostRequest]