import type { PaginatedResponseInterface } from "@/types/pagination";
import type {
	SMSMessageCountGetResponse,
	SMSMessageGetResponse,
} from "@/types/sms_message";
import type { CausalityAssessmentLevelEnum } from "~/types/adr";

const path = "alerts";
type AlertParams = {
	page: number;
	size: number;
	query?: string;
	causality_level?: CausalityAssessmentLevelEnum;
	has_been_sent?: boolean;
};

export async function fetchToBeSentIndividualAlerts(params: AlertParams) {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<
		PaginatedResponseInterface<SMSMessageCountGetResponse>
	>(`/${path}/`, { method: "GET", query: params });
}

export async function fetchAlreadySentIndividualAlerts(params: AlertParams) {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<
		PaginatedResponseInterface<SMSMessageCountGetResponse>
	>(`/${path}/`, { method: "GET", query: params });
}

export async function fetchToBeSentAdditionalInfoAlerts(params: AlertParams) {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<
		PaginatedResponseInterface<SMSMessageCountGetResponse>
	>(`/${path}/`, { method: "GET", query: params });
}

export async function fetchAlreadySentAdditionalInfoAlerts(
	params: AlertParams
) {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<
		PaginatedResponseInterface<SMSMessageCountGetResponse>
	>(`/${path}/`, { method: "GET", query: params });
}

export async function sendIndividualAlert(adrId: string) {
	const { $serverFetch } = useNuxtApp();
	return await $serverFetch<SMSMessageGetResponse[]>(
		"/send_individual_alert",
		{
			method: "POST",
			body: { adr_id: adrId },
		}
	);
}
