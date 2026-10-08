<template>
	<div class="mx-auto max-w-3xl space-y-6">
		<div>
			<h1 class="text-2xl font-bold">API keys</h1>
			<p class="text-sm text-muted">
				Use an API key to call the MediLinda API from scripts. Send it in the
				<code>x-api-key</code> header.
			</p>
		</div>

		<UAlert
			v-if="newKey"
			color="success"
			variant="subtle"
			icon="i-lucide-key-round"
			title="Copy your new key now. It is not shown again."
			:actions="[
				{ label: 'Copy', icon: 'i-lucide-copy', color: 'neutral', onClick: () => copy(newKey!) },
				{ label: 'Done', color: 'neutral', variant: 'outline', onClick: () => (newKey = null) },
			]"
		>
			<template #description>
				<code class="break-all">{{ newKey }}</code>
			</template>
		</UAlert>

		<UAlert
			v-if="apiError"
			color="error"
			variant="subtle"
			icon="i-lucide-triangle-alert"
			:title="apiError"
			close
			@update:open="apiError = null"
		/>

		<UCard>
			<template #header><h2 class="font-semibold">Create a key</h2></template>
			<UForm :state="form" class="flex flex-wrap items-end gap-3" @submit="createKey">
				<UFormField label="Name" name="name" class="grow">
					<UInput v-model="form.name" placeholder="For example: nightly export" class="w-full" />
				</UFormField>
				<UFormField label="Expires in (days)" name="days" help="Leave empty for no expiry.">
					<UInput v-model.number="form.days" type="number" min="1" class="w-40" />
				</UFormField>
				<UButton type="submit" label="Create key" icon="i-lucide-plus" :loading="isCreating" />
			</UForm>
		</UCard>

		<UCard>
			<template #header><h2 class="font-semibold">Your keys</h2></template>

			<div v-if="isLoading" class="space-y-3" aria-busy="true">
				<USkeleton v-for="n in 2" :key="n" class="h-12 w-full" />
			</div>

			<UAlert
				v-else-if="loadError"
				color="error"
				variant="subtle"
				icon="i-lucide-triangle-alert"
				title="Could not load your keys"
				:description="loadError"
				:actions="[{ label: 'Try again', color: 'neutral', onClick: loadKeys }]"
			/>

			<p v-else-if="!keys.length" class="text-sm text-muted">No API keys yet.</p>

			<ul v-else class="divide-y divide-default">
				<li v-for="key in keys" :key="key.id" class="flex items-center justify-between gap-4 py-3">
					<div class="min-w-0">
						<div class="flex items-center gap-2">
							<span class="truncate font-medium">{{ key.name || "Unnamed key" }}</span>
							<UBadge v-if="key.status.expired" color="error" variant="subtle" size="sm">Expired</UBadge>
						</div>
						<div class="text-xs text-muted">
							<span v-if="key.start">{{ key.start }}… · </span>{{ key.status.text }}
						</div>
					</div>
					<UButton
						color="error"
						variant="soft"
						label="Revoke"
						icon="i-lucide-trash-2"
						@click="toRevoke = key"
					/>
				</li>
			</ul>
		</UCard>

		<UCard>
			<template #header><h2 class="font-semibold">Use a key</h2></template>
			<pre class="overflow-x-auto rounded-md bg-elevated p-3 text-sm"><code>curl -H "x-api-key: YOUR_KEY" \
  {{ apiBase }}/api/v1/adrs/</code></pre>
		</UCard>

		<UModal
			:open="!!toRevoke"
			title="Revoke this key?"
			@update:open="(open: boolean) => !open && (toRevoke = null)"
		>
			<template #body>
				<p>
					<strong>{{ toRevoke?.name || "Unnamed key" }}</strong>
					stops working at once. A script that uses it fails. You cannot undo this.
				</p>
			</template>
			<template #footer>
				<div class="flex w-full justify-end gap-2">
					<UButton color="neutral" variant="outline" label="Cancel" :disabled="isRevoking" @click="toRevoke = null" />
					<UButton color="error" label="Revoke" :loading="isRevoking" @click="revokeKey" />
				</div>
			</template>
		</UModal>
	</div>
</template>

<script setup lang="ts">
import { authClient } from "~/lib/auth-client";
import { describeKey, expiryInSeconds } from "~/utils/api-keys";

type RawKey = {
	id: string;
	name: string | null;
	start: string | null;
	expiresAt: Date | string | null;
};
type KeyRow = RawKey & { status: ReturnType<typeof describeKey> };

const toast = useToast();
const apiBase = useRuntimeConfig().public.serverApi;

const keys = ref<KeyRow[]>([]);
const newKey = ref<string | null>(null);
const apiError = ref<string | null>(null);
const loadError = ref<string | null>(null);
const isLoading = ref(true);
const isCreating = ref(false);
const form = reactive<{ name: string; days: number | undefined }>({ name: "", days: 90 });

const toRevoke = ref<KeyRow | null>(null);
const isRevoking = ref(false);

async function loadKeys() {
	loadError.value = null;
	isLoading.value = true;

	const { data, error } = await authClient.apiKey.list();
	isLoading.value = false;

	if (error) {
		loadError.value = error.message || "Check your connection and try again.";
		return;
	}
	// The response is an array or { apiKeys: [...] }, depending on the version.
	const raw = ((Array.isArray(data) ? data : (data as { apiKeys?: RawKey[] } | null)?.apiKeys) ??
		[]) as RawKey[];
	keys.value = raw.map((key) => ({ ...key, status: describeKey(key) }));
}

async function createKey() {
	apiError.value = null;
	isCreating.value = true;

	const { data, error } = await authClient.apiKey.create({
		name: form.name.trim() || undefined,
		expiresIn: expiryInSeconds(form.days),
	});
	isCreating.value = false;

	if (error) {
		apiError.value = error.message || "Could not create the key. Try again.";
		return;
	}
	newKey.value = data?.key ?? null;
	form.name = "";
	await loadKeys();
}

async function revokeKey() {
	if (!toRevoke.value) return;
	isRevoking.value = true;

	const { error } = await authClient.apiKey.delete({ keyId: toRevoke.value.id });
	isRevoking.value = false;

	if (error) {
		apiError.value = error.message || "Could not revoke the key. Try again.";
		toRevoke.value = null;
		return;
	}
	toast.add({ title: "Key revoked", color: "success" });
	toRevoke.value = null;
	await loadKeys();
}

async function copy(value: string) {
	try {
		await navigator.clipboard.writeText(value);
		toast.add({ title: "Key copied", color: "success" });
	} catch {
		toast.add({ title: "Could not copy", description: "Select the key and copy it by hand.", color: "error" });
	}
}

onMounted(loadKeys);
useHead({ title: "API keys | MediLinda" });
</script>
