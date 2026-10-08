<template>
	<div class="space-y-6 max-w-3xl mx-auto">
		<div>
			<h2 class="text-xl font-semibold">API keys</h2>
			<p class="text-sm text-muted">
				Use an API key to call the MediLinda API from scripts. Send it
				in the <code>x-api-key</code> header.
			</p>
		</div>

		<UAlert
			v-if="newKey"
			color="success"
			variant="soft"
			title="Copy your new key now. It will not be shown again."
			:description="newKey"
			:actions="[
				{ label: 'Copy', onClick: () => copy(newKey!) },
				{ label: 'Done', variant: 'outline', onClick: () => (newKey = null) },
			]"
		/>
		<UAlert v-if="apiError" color="error" variant="soft" :title="apiError" />

		<UCard>
			<UForm :state="form" class="flex gap-3 items-end" @submit="createKey">
				<UFormField label="Name" name="name" class="grow">
					<UInput v-model="form.name" placeholder="e.g. nightly export" class="w-full" />
				</UFormField>
				<UFormField label="Expires in (days)" name="days">
					<UInput v-model.number="form.days" type="number" min="1" />
				</UFormField>
				<UButton type="submit" label="Create key" :loading="isCreating" />
			</UForm>
		</UCard>

		<UCard>
			<p v-if="!keys.length" class="text-sm text-muted">No API keys yet.</p>
			<ul v-else class="divide-y divide-default">
				<li v-for="key in keys" :key="key.id" class="flex items-center justify-between py-3">
					<div>
						<div class="font-medium">{{ key.name || "Unnamed key" }}</div>
						<div class="text-xs text-muted">
							{{ key.start }}… ·
							{{ key.expiresAt ? `expires ${new Date(key.expiresAt).toLocaleDateString()}` : "no expiry" }}
						</div>
					</div>
					<UButton
						color="error"
						variant="soft"
						label="Revoke"
						@click="revokeKey(key.id)"
					/>
				</li>
			</ul>
		</UCard>
	</div>
</template>

<script setup lang="ts">
import { authClient } from "~/lib/auth-client";

type KeyRow = {
	id: string;
	name: string | null;
	start: string | null;
	expiresAt: Date | string | null;
};

const keys = ref<KeyRow[]>([]);
const newKey = ref<string | null>(null);
const apiError = ref<string | null>(null);
const isCreating = ref(false);
const form = reactive({ name: "", days: 90 });

async function loadKeys() {
	const { data, error } = await authClient.apiKey.list();
	if (error) {
		apiError.value = error.message || "Could not load API keys.";
		return;
	}
	// Response is either an array or { apiKeys: [...] } depending on version.
	keys.value = (Array.isArray(data) ? data : (data as any)?.apiKeys) ?? [];
}

async function createKey() {
	apiError.value = null;
	isCreating.value = true;
	const { data, error } = await authClient.apiKey.create({
		name: form.name || undefined,
		expiresIn: form.days ? form.days * 24 * 60 * 60 : undefined,
	});
	isCreating.value = false;

	if (error) {
		apiError.value = error.message || "Could not create API key.";
		return;
	}
	newKey.value = data?.key ?? null;
	form.name = "";
	await loadKeys();
}

async function revokeKey(keyId: string) {
	const { error } = await authClient.apiKey.delete({ keyId });
	if (error) {
		apiError.value = error.message || "Could not revoke API key.";
		return;
	}
	await loadKeys();
}

async function copy(value: string) {
	await navigator.clipboard.writeText(value);
}

onMounted(loadKeys);
useHead({ title: "API keys | MediLinda" });
</script>
