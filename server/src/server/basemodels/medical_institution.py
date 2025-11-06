from typing import List

from pydantic import BaseModel, ConfigDict


# Medical Institution
class MedicalInstitutionGetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    mfl_code: str | None = None
    dhis_code: str | None = None
    county: str | None = None
    sub_county: str | None = None


class MedicalInstitutionPostRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    mfl_code: str | None = None
    dhis_code: str | None = None
    county: str | None = None
    sub_county: str | None = None


# Medical Institution Telephone
class MedicalInstitutionTelephoneGetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    medical_institution_id: str
    telephone: str


class MedicalInstitutionTelephonePostRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    medical_institution_id: str
    telephone: str


class MultipleMedicalInstitutionTelephonePostRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    telephones: List[MedicalInstitutionTelephonePostRequest]
