<template>
	<UCard class="mx-auto mt-16 w-full max-w-sm">
		<template #header>
			<h1 class="text-lg font-semibold">Create an account</h1>
		</template>

		<UForm :schema="signupSchema" :state="state" class="space-y-6" @submit="onSubmit">
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
					placeholder="Choose a username"
					icon="i-lucide-user"
					size="lg"
					autofocus
					autocomplete="username"
					class="w-full"
				/>
			</UFormField>

			<div class="grid gap-6 sm:grid-cols-2">
				<UFormField label="First name" name="firstName">
					<UInput
						v-model="state.firstName"
						placeholder="First name"
						size="lg"
						autocomplete="given-name"
						class="w-full"
					/>
				</UFormField>
				<UFormField label="Last name" name="lastName">
					<UInput
						v-model="state.lastName"
						placeholder="Last name"
						size="lg"
						autocomplete="family-name"
						class="w-full"
					/>
				</UFormField>
			</div>

			<UFormField label="Password" name="password" help="Use at least 8 characters.">
				<UInput
					v-model="state.password"
					:type="showPassword ? 'text' : 'password'"
					placeholder="Choose a password"
					icon="i-lucide-lock"
					size="lg"
					autocomplete="new-password"
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
				label="Create account"
				size="lg"
				block
			/>

			<p class="text-center text-sm text-muted">
				Already have an account?
				<ULink to="/auth/login" class="font-medium text-primary">Log in</ULink>
			</p>
		</UForm>
	</UCard>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import { authClient } from "~/lib/auth-client";
import { signupSchema, type SignupForm } from "~/utils/auth-forms";

const state = reactive<Partial<SignupForm>>({
	username: undefined,
	firstName: undefined,
	lastName: undefined,
	password: undefined,
});

const showPassword = ref(false);
const isSubmitting = ref(false);
const apiError = ref<string | null>(null);

async function onSubmit(event: FormSubmitEvent<SignupForm>) {
	apiError.value = null;
	isSubmitting.value = true;

	const { username, password, firstName, lastName } = event.data;

	// Better Auth requires an email. Users log in with their username,
	// so a placeholder address is stored.
	const { error } = await authClient.signUp.email({
		email: `${username.toLowerCase()}@users.medilinda.local`,
		name: `${firstName} ${lastName}`,
		password,
		username,
		firstName,
		lastName,
	} as Parameters<typeof authClient.signUp.email>[0]);

	isSubmitting.value = false;

	if (error) {
		apiError.value = error.message || "Sign-up failed. Try again.";
		return;
	}

	await navigateTo("/adr");
}

definePageMeta({ layout: "auth" });
useHead({ title: "Create an account | MediLinda" });
</script>
