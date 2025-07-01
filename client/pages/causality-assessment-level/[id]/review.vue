<template>
	<p v-if="calStatus == 'pending'">Loading CAL...</p>
	<p v-else-if="calStatus == 'error'">{{ calError }}</p>
	<div v-else-if="calStatus == 'success'" class="page-wrapper">
		<Toaster />
		<CausalityAssessmentLevelComparison
			:value="calData?.causality_assessment_level_value"
		/>
		<Tabs default-value="review">
			<div class="w-max mx-auto">
				<TabsList>
					<TabsTrigger value="adr"
						>Adverse Drug Reaction Report Details</TabsTrigger
					>
					<TabsTrigger value="review">Review Form</TabsTrigger>
				</TabsList>
			</div>

			<TabsContent value="adr">
				<ADRDetails v-if="adrData" :data="adrData" />
			</TabsContent>
			<TabsContent value="review">
				<ADRReviewForm
					:predicted_causality_assessment_level="
						calData?.causality_assessment_level_value
					"
					:causality_assessment_level_id="calData?.id"
					:mode="mode"
				/>
			</TabsContent>
		</Tabs>
		<!-- <p
			v-for="causality_assessment_level in data?.causality_assessment_levels"
		>
			<Card>
				<CardHeader>
					<CardTitle>Causality Assessment Level</CardTitle>
				</CardHeader>
				<CardContent>
					{{
						causality_assessment_level.causality_assessment_level_value
					}}
				</CardContent>
			</Card>
		</p> -->
	</div>
</template>

<script setup lang="ts">
import { Toaster } from "@/components/ui/toast";
import { useToast } from "@/components/ui/toast/use-toast";
import type { ADRGetResponseInterface } from "@/types/adr";
import type { CausalityAssessmentLevelGetResponseInterface } from "@/types/cal";
import type { SMSMessageGetResponse } from "@/types/sms_message";
import type { PaginatedResponseInterface } from "@/types/pagination";
const { toast } = useToast();
const route = useRoute();
const id = route.params.id as string;

type ModeType = "create" | "update";
const mode: ModeType = (route.query.mode as ModeType) || "create"; // If the mode is not set, then the default is create
// Store
const authStore = useAuthStore();

const smsData = ref<PaginatedResponseInterface<SMSMessageGetResponse> | null>(
	null
);
const smsError = ref<unknown | null>(null);
const smsStatus = ref<"idle" | "pending" | "success" | "error">("idle");

const calData = ref<CausalityAssessmentLevelGetResponseInterface | null>(null);
const calError = ref<unknown | null>(null);
const calStatus = ref<"idle" | "pending" | "success" | "error">("idle");

const adrData = ref<ADRGetResponseInterface | null>(null);
const adrError = ref<unknown | null>(null);
const adrStatus = ref<"idle" | "pending" | "success" | "error">("idle");

onMounted(async () => {
	calStatus.value = "pending";
	try {
		const data = await $fetch<CausalityAssessmentLevelGetResponseInterface>(
			`${
				useRuntimeConfig().public.serverApi
			}/causality_assessment_level/${id}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
			}
		);

		if (!data) throw new Error("No causality data received");

		calData.value = data;
		console.log(calData.value.causality_assessment_level_value);
		calStatus.value = "success";

		// // 🔔 Trigger toast if assessment is 'Certain'
		// if (calData.value.causality_assessment_level_value == "certain") {
		// 	toast({
		// 		title: "Causality Level: Certain",
		// 		description:
		// 			"This ADR has been definitively linked to the drug.",
		// 	});
		// }
	} catch (error) {
		calError.value = error;
		calStatus.value = "error";
	}
});

// Now separately fetch ADR after calData is set
watchEffect(async () => {
	if (calData.value?.adr_id) {
		adrStatus.value = "pending";
		try {
			const data = await $fetch<ADRGetResponseInterface>(
				`${useRuntimeConfig().public.serverApi}/adr/${
					calData.value.adr_id
				}`,
				{
					method: "GET",
					headers: {
						Authorization: `Bearer ${authStore.accessToken}`,
					},
				}
			);

			if (!data) throw new Error("No ADR data received");

			adrData.value = data;
			adrStatus.value = "success";
		} catch (error) {
			adrError.value = error;
			adrStatus.value = "error";
		}

		try {
			const data = await $fetch<
				PaginatedResponseInterface<SMSMessageGetResponse>
			>(`${useRuntimeConfig().public.serverApi}/sms_message`, {
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					adr_id: calData.value.adr_id,
				},
			});

			if (!data) throw new Error("No SMS data received");

			smsData.value = data;

			smsData.value.items?.map((sms) => {
				toast({
					title: `${sms.status} - `,
					description: `Number: ${sms.number}\nMessage: ${sms.content}`,
				});
			});
			smsStatus.value = "success";
		} catch (error) {
			smsError.value = error;
			smsStatus.value = "error";
		}
	}
});

useHead({ title: "Review a Causality Assessment Level | MediLinda" });
</script>
