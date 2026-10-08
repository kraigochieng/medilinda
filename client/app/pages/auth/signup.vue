<template>
	<UCard class="w-96 mt-16 mx-auto">
		<template #header>
			<h2>Signup</h2>
		</template>
		<UForm
			:schema="signupValidationSchema"
			:state="signupFormState"
			class="space-y-6"
			@submit="onSubmit"
		>
			<UAlert
				v-if="apiError"
				icon="i-heroicons-exclamation-triangle"
				variant="soft"
				:title="apiError"
				:close-button="{
					icon: 'i-heroicons-x-mark-20-solid',
					color: 'red',
					variant: 'link',
					padded: false,
				}"
				@close="apiError = null"
			/>

			<UFormField label="Username" name="username">
				<UInput
					v-model="signupFormState.username"
					placeholder="Enter Username"
					icon="i-lucide-user"
					size="lg"
					autofocus
					class="w-full"
				/>
			</UFormField>

			<UFormField label="First Name" name="firstName">
				<UInput
					v-model="signupFormState.firstName"
					type="text"
					placeholder="Enter Firstname"
					icon="i-lucide-lock"
					size="lg"
					class="w-full"
				/>
			</UFormField>
			<UFormField label="Last Name" name="lastName">
				<UInput
					v-model="signupFormState.lastName"
					type="text"
					placeholder="Enter Lastname"
					icon="i-lucide-lock"
					size="lg"
					class="w-full"
				/>
			</UFormField>
			<UButton
				type="submit"
				trailing-icon="i-lucide-circle-arrow-right"
				:loading="isSubmitting"
				label="Signup"
				size="lg"
				class="w-full"
				block
			/>
			<div class="w-full flex justify-between">
				<ULink to="/auth/signup">Forgot Password</ULink>
				<ULink to="/auth/login">Login</ULink>
			</div>
		</UForm>
	</UCard>
</template>

<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui";
import { z } from "zod";
import { authClient } from "~/lib/auth-client";

const signupValidationSchema = z.object({
	username: z.string().min(3, "Username must be at least 3 characters"),
	firstName: z.string().min(1, "First name is required"),
	lastName: z.string().min(1, "Last name is required"),
	password: z.string().min(8, "Password must be at least 8 characters"),
});

type signupTypeValidationSchema = z.infer<typeof signupValidationSchema>;

const signupFormState = reactive<Partial<signupTypeValidationSchema>>({
	username: undefined,
	password: undefined,
	firstName: undefined,
	lastName: undefined,
});

const isSubmitting = ref(false);
const apiError = ref<string | null>(null);

async function onSubmit(event: FormSubmitEvent<signupTypeValidationSchema>) {
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
		apiError.value = error.message || "Signup failed. Please try again.";
		return;
	}

	await navigateTo("/adr");
}

definePageMeta({
	layout: "auth",
});
useHead({ title: "Signup | MediLinda" });
</script>
