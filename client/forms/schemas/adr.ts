import * as z from "zod";

export const adrFormValidationSchema = z.object({
	// Personal Details
	medicalInstitutionId: z.string().default("uuid"),
	patientName: z.string().default("Kraig Ochieng"),
	inpatientOrOutpatientNumber: z.string().default("IP-123456"),
	patientDateOfBirth: z.string(),
	patientAge: z.number(),
	patientAddress: z.string().default("Kileleshwa, Nairobi"),
	patientWeightKg: z.number().default(60),
	patientHeightCm: z.number().default(178),
	wardOrClinic: z.string().default("Main Clinic"),
	patientGender: z
		.enum(
			adrFormCategoricalValues["patientGender"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("male"),
	pregnancyStatus: z
		.enum(
			adrFormCategoricalValues["pregnancyStatus"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("not applicable"),
	knownAllergy: z
		.enum(
			adrFormCategoricalValues["knownAllergy"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("no"),
	// SuspeCted Adverse Reaction
	dateOfOnsetOfReaction: z.string(),
	descriptionOfReaction: z.string().default("Very disturbing. Vomiting"),
	// Medicines
	rifampicinSuspected: z.boolean().optional(),
	rifampicinBatchNo: z.string().optional(),
	rifampicinManufacturer: z.string().optional(),
	rifampicinDoseAmount: z.number().optional(),
	rifampicinRoute: z
		.enum(
			adrFormCategoricalValues["route"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("oral"),
	rifampicinFrequencyNumber: z.number().optional(),
	rifampicinStartDate: z.string().optional(),
	rifampicinStopDate: z.string().optional(),

	isoniazidSuspected: z.boolean().optional(),
	isoniazidBatchNo: z.string().optional(),
	isoniazidManufacturer: z.string().optional(),
	isoniazidDoseAmount: z.number().optional(),
	isoniazidRoute: z
		.enum(
			adrFormCategoricalValues["route"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("oral"),
	isoniazidFrequencyNumber: z.number().optional(),
	isoniazidStartDate: z.string().optional(),
	isoniazidStopDate: z.string().optional(),

	pyrazinamideSuspected: z.boolean().optional(),
	pyrazinamideBatchNo: z.string().optional(),
	pyrazinamideManufacturer: z.string().optional(),
	pyrazinamideDoseAmount: z.number().optional(),
	pyrazinamideRoute: z
		.enum(
			adrFormCategoricalValues["route"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("oral"),
	pyrazinamideFrequencyNumber: z.number().optional(),
	pyrazinamideStartDate: z.string().optional(),
	pyrazinamideStopDate: z.string().optional(),

	ethambutolSuspected: z.boolean().optional(),
	ethambutolBatchNo: z.string().optional(),
	ethambutolManufacturer: z.string().optional(),
	ethambutolDoseAmount: z.number().optional(),
	ethambutolRoute: z
		.enum(
			adrFormCategoricalValues["route"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("oral"),
	ethambutolFrequencyNumber: z.number().optional(),
	ethambutolStartDate: z.string().optional(),
	ethambutolStopDate: z.string().optional(),
	// Rechallenge/Dechallenge
	rechallenge: z
		.enum(
			adrFormCategoricalValues["rechallenge"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("yes"),
	dechallenge: z
		.enum(
			adrFormCategoricalValues["dechallenge"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("yes"),
	// Grading od Reaction/Event
	severity: z
		.enum(
			adrFormCategoricalValues["severity"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("mild"),
	isSerious: z
		.enum(
			adrFormCategoricalValues["isSerious"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("no"),
	criteriaForSeriousness: z
		.enum(
			adrFormCategoricalValues["criteriaForSeriousness"].map(
				(x) => x.value
			) as [string, ...string[]]
		)
		.default("hospitalisation"),
	actionTaken: z
		.enum(
			adrFormCategoricalValues["actionTaken"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("unknown"),
	outcome: z
		.enum(
			adrFormCategoricalValues["outcome"].map((x) => x.value) as [
				string,
				...string[]
			]
		)
		.default("recovered"),
	comments: z.string().default("Will be looked into"),
});

export type adrFormTypeValidationSchema = z.infer<
	typeof adrFormValidationSchema
>;
