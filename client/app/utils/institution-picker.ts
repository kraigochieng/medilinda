// Items for the institution picker.
import type { MedicalInstitutionGetResponseInterface as Institution } from "~/types/medical_institution";

export interface InstitutionItem {
	value: string; // the institution id
	label: string; // its name
	location: string; // "Sub-county, County · MFL 12345"
}

export function locationLine(institution: Institution): string {
	const place = [institution.sub_county, institution.county].filter(Boolean).join(", ");
	const code = institution.mfl_code ? `MFL ${institution.mfl_code}` : "";

	return [place, code].filter(Boolean).join(" · ");
}

export function toItem(institution: Institution): InstitutionItem {
	return {
		value: institution.id,
		label: institution.name,
		location: locationLine(institution),
	};
}

// Search results, with the institution that is already chosen included, so it
// still shows when a search no longer finds it.
export function buildItems(
	results: Institution[],
	selected?: Institution | null,
): InstitutionItem[] {
	const items = results.map(toItem);

	if (selected && !items.some((item) => item.value === selected.id)) {
		items.unshift(toItem(selected));
	}

	return items;
}
