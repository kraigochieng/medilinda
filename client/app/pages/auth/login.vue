<template>
	<UCard class="w-96 mt-16 mx-auto">
		<template #header>
			<h2>Login</h2>
		</template>
		<UForm
			:schema="loginValidationSchema"
			:state="loginFormState"
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
					v-model="loginFormState.username"
					placeholder="Enter Username"
					icon="i-lucide-user"
					size="lg"
					autofocus
					class="w-full"
				/>
			</UFormField>

			<UFormField label="Password" name="password">
				<UInput
					v-model="loginFormState.password"
					type="password"
					placeholder="Enter Password"
					icon="i-lucide-lock"
					size="lg"
					class="w-full"
				/>
			</UFormField>
			<UButton
				type="submit"
				trailing-icon="i-lucide-circle-arrow-right"
				:loading="isSubmitting"
				label="Login"
				size="lg"
				class="w-full"
				block
			/>
			<div class="w-full flex justify-between">
				<ULink to="/auth/signup">Forgot Password</ULink>
				<ULink to="/auth/signup">Create a new account</ULink>
			</div>
		</UForm>
	</UCard>
</template>

<script setup lang="ts">
import type { TokenResponse } from "@/types/auth";
import type { FormSubmitEvent } from "@nuxt/ui";
import { z } from "zod";

const loginValidationSchema = z.object({
	username: z.string().min(1, "Username is required"),
	password: z.string().min(1, "Password is required"),
});

type LoginForm = z.output<typeof loginValidationSchema>;

const loginFormState = reactive<Partial<LoginForm>>({
	username: undefined,
	password: undefined,
});

const isSubmitting = ref(false);
const apiError = ref<string | null>(null);

async function onSubmit(event: FormSubmitEvent<LoginForm>) {
	// Reset previous errors and set loading state
	apiError.value = null;
	isSubmitting.value = true;

	try {
		// Use Nuxt's built-in $fetch to make the API call.
		// The body is URL-encoded, which is common for OAuth2 login endpoints.
		const response = await $fetch<TokenResponse>(
			`${useRuntimeConfig().public.serverApi}/api/v1/auth/token`,
			{
				method: "POST",
				body: new URLSearchParams(event.data as Record<string, string>),
				headers: {
					"Content-Type": "application/x-www-form-urlencoded",
				},
			}
		);

		console.log("Login successful:", response);

		const medilindaBearerToken = useCookie<string | null>(
			"medilindaBearerToken"
		);
		medilindaBearerToken.value = response.access_token;

		// On success, redirect the user to their dashboard.
		await navigateTo("/adr");
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
useHead({ title: "Login | MediLinda" });
</script>

<style scoped>
@reference "assets/css/main.css";
</style>
