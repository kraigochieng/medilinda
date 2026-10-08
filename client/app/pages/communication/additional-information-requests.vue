<template>
	<div class="space-y-4">
		<div>
			<h1 class="text-2xl font-bold">Additional info requests</h1>
			<p class="text-sm text-muted">Requests for more information about reports the model could not classify.</p>
		</div>

		<UTabs :items="tabs" color="neutral">
			<template #to-be-sent>
				<SmsQueueTable
					class="mt-4"
					:fetcher="fetchToBeSentAdditionalInfoAlerts"
					:query-key="['alerts', 'alerts-info', 'to-be-sent']"
					causality-level="unclassified"
					:sent="false"
					empty-text="No request is waiting to be sent."
				/>
			</template>
			<template #already-sent>
				<SmsQueueTable
					class="mt-4"
					:fetcher="fetchAlreadySentAdditionalInfoAlerts"
					:query-key="['alerts', 'alerts-info', 'sent']"
					causality-level="unclassified"
					:sent="true"
					empty-text="No request was sent yet."
				/>
			</template>
		</UTabs>
	</div>
</template>

<script setup lang="ts">
import { fetchAlreadySentAdditionalInfoAlerts, fetchToBeSentAdditionalInfoAlerts } from "@/api/sms";
import type { TabsItem } from "@nuxt/ui";

const tabs: TabsItem[] = [
	{ slot: "to-be-sent", label: "To be sent" },
	{ slot: "already-sent", label: "Already sent" },
];

useHead({ title: "Additional info requests | MediLinda" });
</script>
