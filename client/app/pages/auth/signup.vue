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
import type { UserDetails } from "@/types/user";
import type { FormSubmitEvent } from "@nuxt/ui";
import { z } from "zod";

const signupValidationSchema = z.object({
	username: z.string(),
	firstName: z.string(),
	lastName: z.string(),
	password: z.string(),
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
	// Reset previous errors and set loading state
	apiError.value = null;
	isSubmitting.value = true;

	try {
		// Use Nuxt's built-in $fetch to make the API call.
		// The body is URL-encoded, which is common for OAuth2 login endpoints.
		const response = await $fetch<UserDetails>(
			`${useRuntimeConfig().public.serverApi}/api/v1/auth/token`,
			{
				method: "POST",
				body: {
					user_name: event.data.username,
					password: event.data.password,
					first_name: event.data.firstName,
					last_name: event.data.lastName,
				},
			}
		);

		console.log("Signup successful:", response);

		// On success, redirect the user to their dashboard.
		await navigateTo("/auth/login");
	} catch (error: any) {
		// If the API call fails, extract the error message and display it.
		// FastAPI often puts the error details in `error.data.detail`.
		apiError.value =
			error.data?.detail ||
			"An unexpected error occurred. Please try again.";
	} finally {
		// Always reset the loading state, whether the call succeeds or fails.
		isSubmitting.value = false;
	}
}

definePageMeta({
	layout: "auth",
});
useHead({ title: "Signup | MediLinda" });
</script>
