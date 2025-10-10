<template>
	<div class="page-wrapper">
		<div class="flex gap-x-2 justify-between">
			<p class="page-title">Dashboard</p>
			<UButton @mouseup="handlePrint">Print Page</UButton>
		</div>
		<UTabs :items="tabItems">
			<template #overview>
				<div class="flex gap-4 my-8">
					<!-- <UCard v-for="card in summaryCards" :key="card.label">
						<template #header>
							<div
								class="flex justify-between items-center gap-2"
							>
								<p class="text-sm text-muted-foreground">
									{{ card.label }}
								</p>
								<Icon
									:name="card.icon"
									class="w-6 h-6 text-gray-400"
								/>
							</div>
						</template>
						<template #default>
							<p class="text-xl font-bold">{{ card.value }}</p>
						</template>
					</UCard> -->
				</div>
				<div class="chart-group-wrapper">
					<!-- <div>
						<Select
							v-model="selectedYear"
							placeholder="Select year"
							class="w-48"
						>
							<SelectTrigger>
								<SelectValue placeholder="Select year" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem
									v-for="year in availableYears"
									:key="year"
									:value="year"
								>
									{{ year }}
								</SelectItem>
							</SelectContent>
						</Select>
						<ApexChart
							v-if="
								selectedYear &&
								adrMonthlyByYearChart &&
								adrMonthlyByYearChart[selectedYear]
							"
							:options="
								useLineChart(
									`ADRs Reported Monthly - ${selectedYear}`,
									adrMonthlyByYearChart[selectedYear].data,
									adrMonthlyByYearChart[selectedYear].series
								).options
							"
							:series="
								useLineChart(
									`ADRs Reported Monthly - ${selectedYear}`,
									adrMonthlyByYearChart[selectedYear].data,
									adrMonthlyByYearChart[selectedYear].series
								).series
							"
						/>
					</div> -->

					<GraphsReviewedVSUnreviewed />
					<GraphsCausalityDistribution />
					<GraphsApprovalStatus />
					<GraphsTopInstitutions />
					<!-- <GraphsAdrsWeekly /> -->
				</div>
			</template>
			<template #adr>
				<!-- <div class="chart-group-wrapper">
					<ApexChart
						v-for="(chart, index) in adrCategoricalCharts"
						:key="index"
						:options="chart.options"
						:series="chart.series"
					/>
				</div> -->
			</template>
		</UTabs>
	</div>
</template>

<script setup lang="ts">
import type { TabsItem } from "@nuxt/ui";

const tabItems = ref<TabsItem[]>([
	{
		label: "Overview",
		slot: "overview",
	},
	{
		label: "Adverse Drug Reaction",
		slot: "adr",
	},
]);

// const selectedYear = ref(null);
// const availableYears = ref([]);

// const smsMonthlyIndividualAlertChart = ref(null);
// const smsMonthlyAdditionalInfoChart = ref(null);

// const selectedSmsYearIndividualAlert = ref(null);
// const availableSmsYearsIndividualAlert = ref([]);

// const selectedSmsYearAdditionalInfo = ref(null);
// const availableSmsYearsAdditionalInfo = ref([]);

// // Fetch categorical field data and generate charts
// // For ADR categorical field charts
// const adrCategoricalCharts = ref([]);

// // List your categorical fields here exactly as named in the ADRModel
// const adrCategoricalFields = [
// 	"patient_gender",
// 	"known_allergy",
// 	"pregnancy_status",
// 	"rechallenge",
// 	"dechallenge",
// 	"severity",
// 	"is_serious",
// 	"criteria_for_seriousness",
// 	"action_taken",
// 	"outcome",
// ];

onMounted(async () => {
	// const summary = await $fetch(`${serverApi}/dashboard/summary`, { headers });
	// summaryCards.value = [
	// 	{
	// 		label: "Total ADR Reports",
	// 		value: summary?.total_adrs,
	// 		icon: "lucide:file-question",
	// 	},
	// 	{
	// 		label: "Total Medical Institutions Reported From",
	// 		value: summary?.total_institutions,
	// 		icon: "lucide:hospital",
	// 	},
	// ];
});

function handlePrint() {
	window.print();
}

useHead({ title: "Dashboard | MediLinda" });
</script>

<style scoped>
@reference "assets/css/main.css";

.grid-cols-2 > * {
	min-width: 0;
}

.chart-group-wrapper {
	@apply grid grid-cols-1 md:grid-cols-2 gap-6;
}
</style>
