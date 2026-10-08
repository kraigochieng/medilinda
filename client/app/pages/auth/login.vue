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
import type { FormSubmitEvent } from "@nuxt/ui";
import { z } from "zod";
import { authClient } from "~/lib/auth-client";

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
	apiError.value = null;
	isSubmitting.value = true;

	const { error } = await authClient.signIn.username({
		username: event.data.username,
		password: event.data.password,
	});

	isSubmitting.value = false;

	if (error) {
		apiError.value = error.message || "Login failed. Please try again.";
		return;
	}

	await navigateTo("/adr");
}

definePageMeta({
	layout: "auth",
});
useHead({ title: "Login | MediLinda" });
</script>

<style scoped>
@reference "assets/css/main.css";
</style>
