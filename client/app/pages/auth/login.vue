<template>
	<UCard class="mx-auto mt-16 w-full max-w-sm">
		<template #header>
			<h1 class="text-lg font-semibold">Log in</h1>
		</template>

		<UForm :schema="loginSchema" :state="state" class="space-y-6" @submit="onSubmit">
			<UAlert
				v-if="apiError"
				color="error"
				variant="subtle"
				icon="i-lucide-triangle-alert"
				:title="apiError"
				close
				@update:open="apiError = null"
			/>

			<UFormField label="Username" name="username">
				<UInput
					v-model="state.username"
					placeholder="Enter your username"
					icon="i-lucide-user"
					size="lg"
					autofocus
					autocomplete="username"
					class="w-full"
				/>
			</UFormField>

			<UFormField label="Password" name="password">
				<UInput
					v-model="state.password"
					:type="showPassword ? 'text' : 'password'"
					placeholder="Enter your password"
					icon="i-lucide-lock"
					size="lg"
					autocomplete="current-password"
					class="w-full"
					:ui="{ trailing: 'pe-1' }"
				>
					<template #trailing>
						<UButton
							type="button"
							color="neutral"
							variant="link"
							size="sm"
							:icon="showPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
							:aria-label="showPassword ? 'Hide password' : 'Show password'"
							@click="showPassword = !showPassword"
						/>
					</template>
				</UInput>
			</UFormField>

			<UButton
				type="submit"
				trailing-icon="i-lucide-circle-arrow-right"
				:loading="isSubmitting"
				label="Log in"
				size="lg"
				block
			/>

			<p class="text-center text-sm text-muted">
				No account yet?
				<ULink to="/auth/signup" class="font-medium text-primary">Create one</ULink>
			</p>
		</UForm>
	</UCard>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import { authClient } from "~/lib/auth-client";
import { loginSchema, type LoginForm } from "~/utils/auth-forms";

const state = reactive<Partial<LoginForm>>({ username: undefined, password: undefined });

const showPassword = ref(false);
const isSubmitting = ref(false);
const apiError = ref<string | null>(null);

async function onSubmit(event: FormSubmitEvent<LoginForm>) {
	apiError.value = null;
	isSubmitting.value = true;

	const { error } = await authClient.signIn.username({
		username: event.data.username,
		password: event.data.password,
	});

	isSubmitting.value = false;

	if (error) {
		apiError.value = error.message || "Login failed. Try again.";
		return;
	}

	await navigateTo("/adr");
}

definePageMeta({ layout: "auth" });
useHead({ title: "Log in | MediLinda" });
</script>
