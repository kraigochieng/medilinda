import type { SeriesData, MetricValue } from "@/types/dashboard";

const path = "dashboard";

export async function fetchDashboardCausalityDistribution(): Promise<
	MetricValue[]
> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/causality-distribution`);
}
export async function fetchDashboardReviewedUnreviewed(): Promise<
	MetricValue[]
> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/reviewed-unreviewed`);
}

export async function fetchDashboardApprovalStatus(): Promise<MetricValue[]> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/approval-status`);
}

export async function fetchDashboardTopInstitutions(): Promise<MetricValue[]> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/top-institutions`);
}

export async function fetchDashboardAdrsWeekly(): Promise<MetricValue[]> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/adrs-weekly`);
}

export async function fetchDashboardAdrsMonthly(): Promise<MetricValue[]> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/adrs-monthly`);
}

export async function fetchDashboardSmsStatus(): Promise<MetricValue[]> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/sms-status`);
}

export async function fetchDashboardSmsType(): Promise<MetricValue[]> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/sms-type`);
}
export async function fetchDashboardSmsWeekly(): Promise<MetricValue[]> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/sms-weekly`);
}

export async function fetchDashboardSmsMonthly(): Promise<MetricValue[]> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(`/${path}/sms-monthly`);
}

export async function fetchDashboardSmsMonthlyIndividualAlert(): Promise<
	MetricValue[]
> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(
		`/${path}/sms-monthly/individual-alert`
	);
}

export async function fetchDashboardSmsMonthlyAdditionalInfo(): Promise<
	MetricValue[]
> {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<MetricValue[]>(
		`/${path}/sms-monthly/additional-info`
	);
}
