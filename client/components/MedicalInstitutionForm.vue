<template>
	<form @submit.prevent="onSubmit">
		<Card
			:class="{
				'p-0 m-0 border-0 shadow-none': props.isInDialog,
			}"
		>
			<CardHeader>
				<CardTitle> Add an Medical Institution </CardTitle>
				<CardDescription>
					Add an Medical Institution so that it can be part of an ADR
					Report
				</CardDescription>
			</CardHeader>
			<CardContent>
				<FormInput
					type="text"
					name="name"
					label="Institution Name"
					placeholder="Enter institution name"
					description="The official name of the medical institution"
				/>

				<FormInput
					type="text"
					name="mfl_code"
					label="MFL Code"
					placeholder="e.g. 999999"
					description="The Master Facility List (MFL) code of the institution"
				/>

				<FormInput
					type="text"
					name="dhis_code"
					label="DHIS Code"
					placeholder="e.g. DHIS12345"
					description="The District Health Information System (DHIS) code of the institution"
				/>

				<FormInput
					type="text"
					name="county"
					label="County"
					placeholder="e.g. Nairobi"
					description="The county where the institution is located"
				/>

				<FormInput
					type="text"
					name="sub_county"
					label="Sub-County"
					placeholder="e.g. Langata"
					description="The sub-county where the institution is located"
				/>
				<div>
					<Label>Telephone Numbers</Label>
					<div class="flex flex-col gap-2 my-4">
						<div
							v-if="telephoneFields"
							v-for="(phone, index) in telephoneFields"
							:key="phone.key"
							class="flex items-center gap-2"
						>
							<Input
								v-model="phone.value"
								:name="telephoneFields[index].key"
								type="tel"
								pattern="^(\+254(1|7)\d{8}|0(1|7)\d{8})$"
								placeholder="e.g +254712345678 or 0712345678"
								class="flex-1"
								required
							/>
							<ErrorMessage
								:name="`${telephoneFields[index].key}`"
							/>
							<Button
								type="button"
								variant="destructive"
								size="icon"
								@mouseup="removeTelephoneNumber(index)"
								:disabled="telephoneFields.length <= 1"
							>
								-
							</Button>
						</div>

						<Button
							type="button"
							variant="outline"
							class="w-fit mx-auto my-2"
							@mouseup="addTelephoneNumber"
						>
							Add Telephone Number
						</Button>
					</div>
				</div>
			</CardContent>
			<CardFooter>
				<Button id="submit" type="submit" class="w-full mx-auto my-4">{{
					props.mode == "create"
						? "Add Medical Institution"
						: "Edit Medical Institution"
				}}</Button>
			</CardFooter>
		</Card>
	</form>
</template>

<script setup lang="ts">
import humps from "humps";
import FormInput from "./ui/custom/FormInput.vue";
const props = withDefaults(
	defineProps<{
		id?: string;
		mode: "create" | "update";
		isInDialog?: boolean;
	}>(),
	{ isInDialog: false }
);

const emit = defineEmits<{
	(
		e: "submitted",
		success: boolean,
		medicalInstitutionId?: string,
		message?: string
	): void;
}>();

// Lifecycle hooks
onMounted(async () => {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;
	const authStore = useAuthStore();

	// If there is an id
	if (props.id) {
		// Get existing data
		const response =
			await $fetch<medicalInstitutionFormTypeValidationSchema>(
				`${serverApi}/medical_institution/${props.id}`,
				{
					method: "GET",
					headers: {
						Authorization: `Bearer ${authStore.accessToken}`,
					},
				}
			);

		// Pre-fill form
		const camel = humps.camelizeKeys(
			response
		) as medicalInstitutionFormTypeValidationSchema;

		for (const key of Object.keys(camel) as Array<
			keyof medicalInstitutionFormTypeValidationSchema
		>) {
			setFieldValue(key, camel[key]);
		}
	}
});
const {
	values,
	errors,
	defineField,
	handleSubmit,
	isSubmitting,
	setFieldValue,
} = useForm({
	validationSchema: toTypedSchema(medicalInstitutionFormValidationSchema),
	initialValues: {
		telephone_numbers: ["+254777529295", "0787654321"],
	},
});

const [name, nameAttrs] = defineField("name");
const [mfl_code, mfl_codeAttrs] = defineField("mfl_code");
const [dhis_code, dhis_codeAttrs] = defineField("dhis_code");
const [county, countyAttrs] = defineField("county");
const [sub_county, sub_countyAttrs] = defineField("sub_county");

const {
	fields: telephoneFields,
	push,
	remove,
} = useFieldArray<string>("telephone_numbers");

// Add new telephone number
function addTelephoneNumber() {
	push("");
}

// Remove a telephone number
function removeTelephoneNumber(index: number) {
	if (telephoneFields.value.length > 1) {
		remove(index);
	}
}

const onSubmit = handleSubmit(async (values) => {
	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;
	const authStore = useAuthStore();

	if (props.mode == "create") {
		const { data, status, error } =
			await useFetch<MedicalInstitutionPostResponseInterface>(
				`${serverApi}/medical_institution`,
				{
					method: "POST",
					headers: {
						Authorization: `Bearer ${authStore.accessToken}`,
					},
					body: {
						name: values["name"],
						mfl_code: values["mfl_code"],
						dhis_code: values["dhis_code"],
						county: values["county"],
						subcounty: values["sub_county"],
					},
				}
			);
		if (status.value === "success" && data.value) {
			const medicalInstitutionId = data.value.id; // or whatever field contains the ID
			const telephonePayload = values.telephone_numbers.map((phone) => ({
				medical_institution_id: medicalInstitutionId,
				telephone: phone,
			}));

			console.log("telephonePayload", telephonePayload);

			const {
				data: telData,
				status: telStatus,
				error: telError,
			} = await useFetch(
				`${serverApi}/medical_institution_telephone`, // or your correct endpoint
				{
					method: "POST",
					headers: {
						Authorization: `Bearer ${authStore.accessToken}`,
					},
					body: {
						telephones: telephonePayload,
					},
				}
			);

			if (telStatus.value === "success") {
				console.log("Telephones added successfully!");
				emit("submitted", true, data.value.id);
			} else {
				console.error("Failed to add telephones:", telError.value);
				emit("submitted", false);
			}
		}
	} else if (props.mode == "update") {
		const { data, status, error } =
			await useFetch<MedicalInstitutionPostResponseInterface>(
				`${serverApi}/medical_institution/${props.id}`,
				{
					method: "PUT",
					headers: {
						Authorization: `Bearer ${authStore.accessToken}`,
					},
					body: humps.decamelizeKeys(values),
				}
			);

		// if (status.value == "success" && data.value) {
		// 	const {
		// 		data: calData,
		// 		status: calStatus,
		// 		error,
		// 	} = await useFetch<PaginatedCausalityAssessmentLevel>(
		// 		`${serverApi}/adr/${data.value.id}/causality_assessment_level`,
		// 		{
		// 			method: "GET",
		// 			headers: {
		// 				Authorization: `Bearer ${authStore.accessToken}`,
		// 			},
		// 			params: {
		// 				page: 1,
		// 				size: 50,
		// 			},
		// 		}
		// 	);

		// 	if (calStatus.value == "success" && calData.value?.items) {
		// 		navigateTo(
		// 			`/causality-assessment-level/${calData.value.items[0].id}/review`
		// 		);
		// 	}
		// }
	}
});
</script>
