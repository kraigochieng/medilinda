export function useFeatureNameFormatter(
	featureName: string
): string | undefined {
	switch (featureName) {
		case "known_allergy_no":
			return "Known Allergy (No)";
		case "known_allergy_yes":
			return "Known Allergy (Yes)";

		case "dechallenge_na":
			return "Dechallenge (N/A)";
		case "dechallenge_no":
			return "Dechallenge (No)";
		case "dechallenge_unknown":
			return "Dechallenge (Unknown)";
		case "dechallenge_yes":
			return "Dechallenge (Yes)";

		case "rechallenge_na":
			return "Rechallenge (N/A)";
		case "rechallenge_no":
			return "Rechallenge (No)";
		case "rechallenge_unknown":
			return "Rechallenge (Unknown)";
		case "rechallenge_yes":
			return "Rechallenge (Yes)";

		case "severity_fatal":
			return "Severity (Fatal)";
		case "severity_mild":
			return "Severity (Mild)";
		case "severity_moderate":
			return "Severity (Moderate)";
		case "severity_severe":
			return "Severity (Severe)";
		case "severity_unknown":
			return "Severity (Unknown)";

		case "is_serious_no":
			return "Is Serious (No)";
		case "is_serious_yes":
			return "Is Serious (Yes)";

		case "criteria_for_seriousness_congenital anomaly":
			return "Seriousness: Congenital Anomaly";
		case "criteria_for_seriousness_death":
			return "Seriousness: Death";
		case "criteria_for_seriousness_disability":
			return "Seriousness: Disability";
		case "criteria_for_seriousness_hospitalisation":
			return "Seriousness: Hospitalisation";
		case "criteria_for_seriousness_life-threatening":
			return "Seriousness: Life-Threatening";

		case "action_taken_dose increased":
			return "Action Taken: Dose Increased";
		case "action_taken_dose not changed":
			return "Action Taken: Dose Not Changed";
		case "action_taken_dose reduced":
			return "Action Taken: Dose Reduced";
		case "action_taken_drug withdrawn":
			return "Action Taken: Drug Withdrawn";
		case "action_taken_not applicable":
			return "Action Taken: Not Applicable";
		case "action_taken_unknown":
			return "Action Taken: Unknown";

		case "outcome_death":
			return "Outcome: Death";
		case "outcome_not recovered":
			return "Outcome: Not Recovered";
		case "outcome_recovered":
			return "Outcome: Recovered";
		case "outcome_recovered with sequelae":
			return "Outcome: Recovered with Sequelae";
		case "outcome_recovering":
			return "Outcome: Recovering";
		case "outcome_unknown":
			return "Outcome: Unknown";

		case "num_suspected_drugs_1":
			return "No. of Suspected Drugs (1)";
		case "num_suspected_drugs_2":
			return "No. of Suspected Drugs (2)";
		case "num_suspected_drugs_3":
			return "No. of Suspected Drugs (3)";

		case "patient_age":
			return "Patient Age";
		case "patient_bmi":
			return "Patient BMI";

		case "rifampicin_start_to_onset_days":
			return "Rifampicin: Start to Onset (days)";
		case "rifampicin_stop_to_onset_days":
			return "Rifampicin: Stop to Onset (days)";
		case "rifampicin_start_stop_difference":
			return "Rifampicin: Start–Stop Diff. (days)";

		case "isoniazid_start_to_onset_days":
			return "Isoniazid: Start to Onset (days)";
		case "isoniazid_stop_to_onset_days":
			return "Isoniazid: Stop to Onset (days)";
		case "isoniazid_start_stop_difference":
			return "Isoniazid: Start–Stop Diff. (days)";

		case "pyrazinamide_start_to_onset_days":
			return "Pyrazinamide: Start to Onset (days)";
		case "pyrazinamide_stop_to_onset_days":
			return "Pyrazinamide: Stop to Onset (days)";
		case "pyrazinamide_start_stop_difference":
			return "Pyrazinamide: Start–Stop Diff. (days)";

		case "ethambutol_start_to_onset_days":
			return "Ethambutol: Start to Onset (days)";
		case "ethambutol_stop_to_onset_days":
			return "Ethambutol: Stop to Onset (days)";
		case "ethambutol_start_stop_difference":
			return "Ethambutol: Start–Stop Diff. (days)";

		case "rifampicin_suspected":
			return "Rifampicin Suspected";
		case "isoniazid_suspected":
			return "Isoniazid Suspected";
		case "pyrazinamide_suspected":
			return "Pyrazinamide Suspected";
		case "ethambutol_suspected":
			return "Ethambutol Suspected";

		default:
			return featureName;
	}
}
