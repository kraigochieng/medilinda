<template>
	<div class="space-y-4">
		<div>
			<h1 class="text-2xl font-bold">Individual alerts</h1>
			<p class="text-sm text-muted">Alerts about reports predicted as certain, sent to the institution.</p>
		</div>

		<UTabs :items="tabs" color="neutral">
			<template #to-be-sent>
				<SmsQueueTable
					class="mt-4"
					:fetcher="fetchToBeSentIndividualAlerts"
					:query-key="['alerts', 'alerts-individual', 'to-be-sent']"
					causality-level="certain"
					:sent="false"
					empty-text="No alert is waiting to be sent."
				/>
			</template>
			<template #already-sent>
				<SmsQueueTable
					class="mt-4"
					:fetcher="fetchAlreadySentIndividualAlerts"
					:query-key="['alerts', 'alerts-individual', 'sent']"
					causality-level="certain"
					:sent="true"
					empty-text="No alert was sent yet."
				/>
			</template>
		</UTabs>
	</div>
</template>

<script setup lang="ts">
import { fetchAlreadySentIndividualAlerts, fetchToBeSentIndividualAlerts } from "@/api/sms";
import type { TabsItem } from "@nuxt/ui";

const tabs: TabsItem[] = [
	{ slot: "to-be-sent", label: "To be sent" },
	{ slot: "already-sent", label: "Already sent" },
];

useHead({ title: "Individual alerts | MediLinda" });
</script>
