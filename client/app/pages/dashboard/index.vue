<template>
	<div class="page-wrapper">
		<div class="flex gap-x-2 justify-between">
			<p class="page-title">Dashboard</p>
			<Button @mouseup="handlePrint">Print Page</Button>
		</div>

		<Tabs default-value="overview">
			<TabsList>
				<TabsTrigger value="overview">Overview</TabsTrigger>
				<TabsTrigger value="adr">Adverse Drug Reaction</TabsTrigger>
				<!-- <TabsTrigger value="sms">SMS</TabsTrigger> -->
			</TabsList>
			<TabsContent value="overview">
				<div class="flex gap-4 my-8">
					<Card v-for="card in summaryCards" :key="card.label">
						<CardHeader>
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
						</CardHeader>
						<CardContent>
							<p class="text-xl font-bold">{{ card.value }}</p>
						</CardContent>
					</Card>
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
					<ApexChart
						v-if="causalityDistributionChart"
						:options="causalityDistributionChart.options"
						:series="causalityDistributionChart.series"
					/>
					<ApexChart
						v-if="reviewedUnreviewedChart"
						:options="reviewedUnreviewedChart.options"
						:series="reviewedUnreviewedChart.series"
					/>
					<ApexChart
						v-if="approvalStatusChart"
						:options="approvalStatusChart.options"
						:series="approvalStatusChart.series"
					/>
					<ApexChart
						v-if="topInstitutionsChart"
						:options="topInstitutionsChart.options"
						:series="topInstitutionsChart.series"
					/>
					<!-- <ApexChart
						v-if="adrWeeklyChart"
						:options="adrWeeklyChart.options"
						:series="adrWeeklyChart.series"
					/> -->
				</div>
			</TabsContent>
			<TabsContent value="adr">
				<div class="chart-group-wrapper">
					<ApexChart
						v-for="(chart, index) in adrCategoricalCharts"
						:key="index"
						:options="chart.options"
						:series="chart.series"
					/>
				</div>
			</TabsContent>
			<!-- <TabsContent value="sms">
				<div class="chart-group-wrapper space-y-6">
					<div>
						<h3 class="mb-2 font-semibold">
							Individual Alert SMS (Monthly)
						</h3>
						<Select
							v-model="selectedSmsYearIndividualAlert"
							placeholder="Select year"
							class="w-48 mb-4"
						>
							<SelectTrigger>
								<SelectValue placeholder="Select year" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem
									v-for="year in availableSmsYearsIndividualAlert"
									:key="year"
									:value="year"
								>
									{{ year }}
								</SelectItem>
							</SelectContent>
						</Select>

						<ApexChart
							v-if="
								selectedSmsYearIndividualAlert &&
								smsMonthlyIndividualAlertChart &&
								smsMonthlyIndividualAlertChart[
									selectedSmsYearIndividualAlert
								]
							"
							:options="
								useLineChart(
									`Individual Alert SMS - ${selectedSmsYearIndividualAlert}`,
									smsMonthlyIndividualAlertChart[
										selectedSmsYearIndividualAlert
									].data,
									smsMonthlyIndividualAlertChart[
										selectedSmsYearIndividualAlert
									].series
								).options
							"
							:series="
								useLineChart(
									`Individual Alert SMS - ${selectedSmsYearIndividualAlert}`,
									smsMonthlyIndividualAlertChart[
										selectedSmsYearIndividualAlert
									].data,
									smsMonthlyIndividualAlertChart[
										selectedSmsYearIndividualAlert
									].series
								).series
							"
						/>
					</div>

					
					<div>
						<h3 class="mb-2 font-semibold">
							Additional Info SMS (Monthly)
						</h3>
						<Select
							v-model="selectedSmsYearAdditionalInfo"
							placeholder="Select year"
							class="w-48 mb-4"
						>
							<SelectTrigger>
								<SelectValue placeholder="Select year" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem
									v-for="year in availableSmsYearsAdditionalInfo"
									:key="year"
									:value="year"
								>
									{{ year }}
								</SelectItem>
							</SelectContent>
						</Select>

						<ApexChart
							v-if="
								selectedSmsYearAdditionalInfo &&
								smsMonthlyAdditionalInfoChart &&
								smsMonthlyAdditionalInfoChart[
									selectedSmsYearAdditionalInfo
								]
							"
							:options="
								useLineChart(
									`Additional Info SMS - ${selectedSmsYearAdditionalInfo}`,
									smsMonthlyAdditionalInfoChart[
										selectedSmsYearAdditionalInfo
									].data,
									smsMonthlyAdditionalInfoChart[
										selectedSmsYearAdditionalInfo
									].series
								).options
							"
							:series="
								useLineChart(
									`Additional Info SMS - ${selectedSmsYearAdditionalInfo}`,
									smsMonthlyAdditionalInfoChart[
										selectedSmsYearAdditionalInfo
									].data,
									smsMonthlyAdditionalInfoChart[
										selectedSmsYearAdditionalInfo
									].series
								).series
							"
						/>
					</div>
					<ApexChart
						v-if="smsStatusChart"
						:options="smsStatusChart.options"
						:series="smsStatusChart.series"
					/>
				</div>
			</TabsContent> -->
		</Tabs>
	</div>
</template>

<script setup>
const authStore = useAuthStore();
const serverApi = useRuntimeConfig().public.serverApi;
const headers = { Authorization: `Bearer ${authStore.accessToken}` };

const summaryCards = ref([]);
const reviewedUnreviewedChart = ref(null);
const causalityDistributionChart = ref(null);
const approvalStatusChart = ref(null);
const topInstitutionsChart = ref(null);
const adrWeeklyChart = ref(null);
const adrMonthlyByYearChart = ref(null);
const smsStatusChart = ref(null);

const selectedYear = ref(null);
const availableYears = ref([]);

const smsMonthlyIndividualAlertChart = ref(null);
const smsMonthlyAdditionalInfoChart = ref(null);

const selectedSmsYearIndividualAlert = ref(null);
const availableSmsYearsIndividualAlert = ref([]);

const selectedSmsYearAdditionalInfo = ref(null);
const availableSmsYearsAdditionalInfo = ref([]);

// Fetch categorical field data and generate charts
// For ADR categorical field charts
const adrCategoricalCharts = ref([]);

// List your categorical fields here exactly as named in the ADRModel
const adrCategoricalFields = [
	"patient_gender",
	"known_allergy",
	"pregnancy_status",
	"rechallenge",
	"dechallenge",
	"severity",
	"is_serious",
	"criteria_for_seriousness",
	"action_taken",
	"outcome",
];

function cleanEnumLabel(label) {
	if (!label) return "";
	// Remove everything before last dot (.) if present
	const parts = label.split(".");
	return parts.length > 1 ? parts[parts.length - 1] : label;
}

onMounted(async () => {
	// const [
	// 	summary,
	// 	reviewedUnreviewed,
	// 	causalityDistribution,
	// 	approvalStatus,
	// 	topInstitutions,
	// 	adrWeekly,
	// 	adrMonthlyByYear,
	// ] = await Promise.all([
	// 	$fetch(`${serverApi}/dashboard/summary`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/reviewed-unreviewed`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/causality-distribution`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/approval-status`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/top-institutions`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/adrs-weekly`, { headers }),
	// 	$fetch(`${serverApi}/dashboard/adrs-monthly`, { headers }),
	// ]);
	const summary = await $fetch(`${serverApi}/dashboard/summary`, { headers });

	const { data: reviewedUnreviewed } = await useFetch(
		`${serverApi}/dashboard/reviewed-unreviewed`,
		{
			headers,
			cache: "no-store",
		}
	);

	const { data: causalityDistribution } = await useFetch(
		`${serverApi}/dashboard/causality-distribution`,
		{
			headers,
			cache: "no-store",
		}
	);

	const { data: approvalStatus } = await useFetch(
		`${serverApi}/dashboard/approval-status`,
		{
			headers,
			cache: "no-store",
		}
	);

	const { data: topInstitutions } = await useFetch(
		`${serverApi}/dashboard/top-institutions`,
		{
			headers,
			cache: "no-store",
		}
	);

	const { data: adrWeekly } = await useFetch(
		`${serverApi}/dashboard/adrs-weekly`,
		{
			headers,
			cache: "no-store",
		}
	);

	const { data: adrMonthlyByYear } = await useFetch(
		`${serverApi}/dashboard/adrs-monthly`,
		{
			headers,
			cache: "no-store",
		}
	);

	const { data: smsStatus } = await useFetch(
		`${serverApi}/dashboard/sms-status`,
		{
			headers,
			cache: "no-store",
		}
	);

	const { data: smsMonthlyIndividualAlert } = await useFetch(
		`${serverApi}/dashboard/sms-monthly/individual-alert`,
		{ headers }
	);
	if (smsMonthlyIndividualAlert.value) {
		smsMonthlyIndividualAlertChart.value = smsMonthlyIndividualAlert.value;
		availableSmsYearsIndividualAlert.value = Object.keys(
			smsMonthlyIndividualAlert.value
		);
		selectedSmsYearIndividualAlert.value =
			availableSmsYearsIndividualAlert.value[0];
	}

	// Additional info monthly data
	const { data: smsMonthlyAdditionalInfo } = await useFetch(
		`${serverApi}/dashboard/sms-monthly/additional-info`,
		{ headers }
	);
	if (smsMonthlyAdditionalInfo.value) {
		smsMonthlyAdditionalInfoChart.value = smsMonthlyAdditionalInfo.value;
		availableSmsYearsAdditionalInfo.value = Object.keys(
			smsMonthlyAdditionalInfo.value
		);
		selectedSmsYearAdditionalInfo.value =
			availableSmsYearsAdditionalInfo.value[0];
	}

	if (adrMonthlyByYear.value) {
		availableYears.value = Object.keys(adrMonthlyByYear.value);
		selectedYear.value = availableYears.value[0]; // default to first year
	}

	summaryCards.value = [
		{
			label: "Total ADR Reports",
			value: summary?.total_adrs,
			icon: "lucide:file-question",
		},
		{
			label: "Total Medical Institutions Reported From",
			value: summary?.total_institutions,
			icon: "lucide:hospital",
		},
	];

	reviewedUnreviewedChart.value = reviewedUnreviewed.value
		? useBarChart(
				"Reviewed ADRs vs Unreviewed ADRs",
				reviewedUnreviewed.value.data,
				reviewedUnreviewed.value.series
		  )
		: null;

	let cleanedCausalityLabels = [];
	if (causalityDistribution.value) {
		cleanedCausalityLabels =
			causalityDistribution.value.data.map(cleanEnumLabel);
	}

	causalityDistributionChart.value = causalityDistribution.value
		? useBarChart(
				"Causality Assessment Distribution",
				cleanedCausalityLabels,
				causalityDistribution.value.series
		  )
		: null;
	approvalStatusChart.value = approvalStatus.value
		? useBarChart(
				"Approved ADRs VS Unapproved ADRs",
				approvalStatus.value.data,
				approvalStatus.value.series
		  )
		: null;
	topInstitutionsChart.value = topInstitutions.value
		? useBarChart(
				"Top Reporting Institutions",
				topInstitutions.value.data,
				topInstitutions.value.series
		  )
		: null;
	adrWeeklyChart.value = adrWeekly.value
		? useBarChart(
				"ADRs Reported Weekly",
				adrWeekly.value.data,
				adrWeekly.value.series
		  )
		: null;

	adrMonthlyByYearChart.value = adrMonthlyByYear.value;

	adrCategoricalCharts.value = [];

	for (const field of adrCategoricalFields) {
		const { data } = await useFetch(
			`${serverApi}/dashboard/categorical-field/${field}`,
			{ headers }
		);
		if (data.value) {
			// Clean labels
			const cleanedLabels = data.value.data.map(cleanEnumLabel);
			adrCategoricalCharts.value.push(
				useBarChart(
					field
						.replace(/_/g, " ")
						.replace(/\b\w/g, (c) => c.toUpperCase()),
					cleanedLabels,
					data.value.series
				)
			);
		}
	}
});

function handlePrint() {
	window.print();
}

useHead({ title: "Dashboard | MediLinda" });
</script>

<style scoped>
.grid-cols-2 > * {
	min-width: 0;
}

.chart-group-wrapper {
	@apply grid grid-cols-1 md:grid-cols-2 gap-6;
}
</style>
