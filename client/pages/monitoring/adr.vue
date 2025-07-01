<template>
	<h1 class="text-center text-3xl font-bold p-4">Summary Statistics</h1>
	<div class="flex gap-4 items-center p-4">
		<DateRangePicker label="Choose Date Range" v-model="dateRange" />
		<Select v-model="timeFrame">
			<SelectTrigger>
				<SelectValue placeholder="Choose a Time Frame" />
			</SelectTrigger>
			<SelectContent>
				<SelectGroup>
					<SelectItem value="today">Today</SelectItem>
					<SelectItem value="last-week">Last Week</SelectItem>
					<SelectItem value="last-1-month">Last 1 Month</SelectItem>
					<SelectItem value="last-3-months">Last 3 Months</SelectItem>
					<SelectItem value="last-6-months">Last 6 Months</SelectItem>
					<SelectItem value="last-1-year">Last 1 Year</SelectItem>
					<SelectItem value="last-2-years">Last 2 Years</SelectItem>
					<SelectItem value="last-5-years">Last 5 Years</SelectItem>
				</SelectGroup>
			</SelectContent>
		</Select>
	</div>
	<div v-if="status == 'success'">
		<div class="flex flex-wrap gap-4 m-4">
			<div class="chart-wrapper">
				<ApexChart
					:options="genderProportionsChart?.options"
					:series="genderProportionsChart?.series"
				></ApexChart>
			</div>
			<div class="chart-wrapper">
				<ApexChart
					:options="pregnancyStatusProportionsChart?.options"
					:series="pregnancyStatusProportionsChart?.series"
				></ApexChart>
			</div>
			<div class="chart-wrapper">
				<ApexChart
					:options="knownChallengeProportionsChart?.options"
					:series="knownChallengeProportionsChart?.series"
				></ApexChart>
			</div>
			<div class="chart-wrapper">
				<ApexChart
					:options="dechallengeProportionsChart?.options"
					:series="dechallengeProportionsChart?.series"
				></ApexChart>
			</div>
			<div class="chart-wrapper">
				<ApexChart
					:options="rechallengeProportionsChart?.options"
					:series="rechallengeProportionsChart?.series"
				></ApexChart>
			</div>
			<div class="chart-wrapper">
				<ApexChart
					:options="severityProportionsChart?.options"
					:series="severityProportionsChart?.series"
				></ApexChart>
			</div>
			<div class="chart-wrapper">
				<ApexChart
					:options="criteriaForSeriousnessProportionsChart?.options"
					:series="criteriaForSeriousnessProportionsChart?.series"
				></ApexChart>
			</div>
			<div class="chart-wrapper">
				<ApexChart
					:options="isSeriousProportionsChart?.options"
					:series="isSeriousProportionsChart?.series"
				></ApexChart>
			</div>
			<div class="chart-wrapper">
				<ApexChart
					:options="outcomeProportionsChart?.options"
					:series="outcomeProportionsChart?.series"
				></ApexChart>
			</div>
		</div>
	</div>
	<p v-else="status == 'error'">{{ error }}</p>
</template>

<script setup lang="ts">
import DateRangePicker from "@/components/ui/custom/DateRangePicker.vue";
import { CalendarDate, getLocalTimeZone, today } from "@internationalized/date";
import type { ApexOptions } from "apexcharts";
import type { DateRange } from "reka-ui";

// Interfaces
interface Proportions {
	series: string[];
	data: number[];
}

interface MonitoringData {
	gender_proportions: Proportions;
	pregnancy_status_proportions: Proportions;
	known_allergy_proportions: Proportions;
	dechallenge_proportions: Proportions;
	rechallenge_proportions: Proportions;
	severity_proportions: Proportions;
	criteria_for_seriousness_proportions: Proportions;
	is_serious_proportions: Proportions;
	outcome_proportions: Proportions;
}
// State
const data = ref<MonitoringData | null>(null);
const status = ref<"pending" | "success" | "error">("pending");
const error = ref<string | null>(null);

// Stores
const authStore = useAuthStore();

// Lifecycle Hooks
onMounted(async () => {
	await fetchMonitoringData();
});

const fetchMonitoringData = async () => {
	try {
		status.value = "pending";
		// Using $fetch for API call
		data.value = await $fetch(
			`${useRuntimeConfig().public.serverApi}/adr_monitoring`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
				},
				params: {
					start: dateRange.value.start?.toString(),
					end: dateRange.value.end?.toString(),
				},
			}
		);

		status.value = "success";
	} catch (err: any) {
		status.value = "error";
		error.value = err.message || "Something went wrong";
	}
};

// Graphs

interface BarChart {
	options: ApexOptions;
	series: ApexAxisChartSeries;
}

interface PieChart {
	options: ApexOptions;
	series: Array<number>;
}

// Charts
const genderProportionsChart = ref<PieChart | null>(null);
const pregnancyStatusProportionsChart = ref<BarChart | null>(null);
const knownChallengeProportionsChart = ref<BarChart | null>(null);
const dechallengeProportionsChart = ref<BarChart | null>(null);
const rechallengeProportionsChart = ref<BarChart | null>(null);
const severityProportionsChart = ref<BarChart | null>(null);
const criteriaForSeriousnessProportionsChart = ref<BarChart | null>(null);
const isSeriousProportionsChart = ref<PieChart | null>(null);
const outcomeProportionsChart = ref<BarChart | null>(null);

watchEffect(() => {
	if (!data.value) return;
	genderProportionsChart.value = usePieChart(
		"Gender Proportions",
		data.value.gender_proportions.series,
		data.value.gender_proportions.data
	);

	pregnancyStatusProportionsChart.value = useBarChart(
		"Pregnancy Status Proportions",
		data.value.pregnancy_status_proportions.series,
		data.value.pregnancy_status_proportions.data
	);

	knownChallengeProportionsChart.value = useBarChart(
		"Known Allergy Proportions",
		data.value.known_allergy_proportions.series,
		data.value.known_allergy_proportions.data
	);

	dechallengeProportionsChart.value = useBarChart(
		"Dechallenge Proportions",
		data.value.dechallenge_proportions.series,
		data.value.dechallenge_proportions.data
	);

	rechallengeProportionsChart.value = useBarChart(
		"Rechallenge Proportions",
		data.value.rechallenge_proportions.series,
		data.value.rechallenge_proportions.data
	);

	severityProportionsChart.value = useBarChart(
		"Severity Proportions",
		data.value.severity_proportions.series,
		data.value.severity_proportions.data
	);

	criteriaForSeriousnessProportionsChart.value = useBarChart(
		"Criteria For Seriousness Proportions",
		data.value.criteria_for_seriousness_proportions.series,
		data.value.criteria_for_seriousness_proportions.data
	);

	isSeriousProportionsChart.value = usePieChart(
		"Is Serious Proportions",
		data.value.is_serious_proportions.series,
		data.value.is_serious_proportions.data
	);

	outcomeProportionsChart.value = useBarChart(
		"Outcome Proportions",
		data.value.outcome_proportions.series,
		data.value.outcome_proportions.data
	);
});
const end = today(getLocalTimeZone());
const start = end.subtract({ months: 1 });

const dateRange = ref({
	start: start,
	end: end,
}) as Ref<DateRange>;

const timeFrame = ref<string>("last-1-month");

// Handle Timeframe Dropdown
watch(timeFrame, (newTimeFrame) => {
	let start = new CalendarDate(2025, 1, 1);
	let end = new CalendarDate(2025, 1, 1);

	if (newTimeFrame == "today") {
		end = today(getLocalTimeZone());
		start = today(getLocalTimeZone());
	} else if (newTimeFrame == "last-week") {
		end = today(getLocalTimeZone());
		start = end.subtract({ weeks: 1 });
	} else if (newTimeFrame == "last-1-month") {
		end = today(getLocalTimeZone());
		start = end.subtract({ months: 1 });
	} else if (newTimeFrame == "last-3-months") {
		end = today(getLocalTimeZone());
		start = end.subtract({ months: 3 });
	} else if (newTimeFrame == "last-6-months") {
		end = today(getLocalTimeZone());
		start = end.subtract({ months: 6 });
	} else if (newTimeFrame == "last-1-year") {
		end = today(getLocalTimeZone());
		start = end.subtract({ years: 1 });
	} else if (newTimeFrame == "last-2-years") {
		end = today(getLocalTimeZone());
		start = end.subtract({ years: 2 });
	} else if (newTimeFrame == "last-5-years") {
		end = today(getLocalTimeZone());
		start = end.subtract({ years: 5 });
	}

	dateRange.value.start = start;
	dateRange.value.end = end;
});

// Resend to API when
watchEffect(async () => {
	if (dateRange.value) {
		await fetchMonitoringData();
	}
});

useHead({ title: "Monitoring | MediLinda" });
</script>

<style scoped>
.chart-wrapper {
	@apply w-full max-w-[600px] border rounded-md;
}
</style>
