export interface MedicalInstitutionPostRequestInterface {
	name: string;
	mfl_code?: string;
	dhis_code?: string;
	county?: string;
	sub_county?: string;
}

export interface MedicalInstitutionPostResponseInterface {
    id: string;
	name: string;
	mfl_code?: string;
	dhis_code?: string;
	county?: string;
	sub_county?: string;
}

export interface MedicalInstitutionGetResponseInterface {
    id: string;
	name: string;
	mfl_code?: string;
	dhis_code?: string;
	county?: string;
	sub_county?: string;
}