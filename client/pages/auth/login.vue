<template>
	<form @submit.prevent="onSubmit" class="my-16 mx-auto w-96">
		<Card>
			<CardHeader><CardTitle>Login</CardTitle></CardHeader>
			<CardContent>
				<FormInput
					type="text"
					name="username"
					label="Username"
					placeholder="Enter Username"
					ref="usernameInputRef"
				/>
				<FormInput
					type="password"
					name="password"
					label="Password"
					placeholder="Enter Password"
				/>
			</CardContent>
			<CardFooter class="flex justify-between px-6 pb-6">
				<Button type="submit">Login</Button>
				<Button variant="ghost"
					><NuxtLink to="/auth/signup"
						>Create a new account</NuxtLink
					></Button
				>
			</CardFooter>
		</Card>
	</form>
</template>
<script setup lang="ts">
import FormInput from "@/components/ui/custom/FormInput.vue";
import type { ComponentPublicInstance } from "vue";

// Stores
const authStore = useAuthStore();

const { values, errors, handleSubmit, defineField, isSubmitting } = useForm({
	validationSchema: toTypedSchema(loginValidationSchema),
});

const [username, usernameAttrs] = defineField("username");
const [password, passwordAttrs] = defineField("password");

const runtimeConfig = useRuntimeConfig();
const serverApi = runtimeConfig.public.serverApi;

const onSubmit = handleSubmit(async (values) => {
	// const {data} = useFetch<TokenResponse>(`${serverApi}/login`, {
	// 	method: "POST",
	// 	body:
	// })

	// const { data } = await postToken(values);
	// if (data.value) {
	// 	localStorage.setItem("accessToken", data.value.accessToken);
	// }
	authStore.login(values);
});

definePageMeta({
	layout: "auth",
});

// const usernameInputRef = ref<ComponentPublicInstance | null>(null);
const usernameInputRef = ref<{ focus: () => void } | null>(null);
onMounted(() => {
	console.log(usernameInputRef.value);
	// Focus the inner input element
	// const nativeInput = usernameInputRef.value?.$el?.querySelector("input");
	// nativeInput?.focus();
	usernameInputRef.value?.focus();
});

useHead({ title: "Login | MediLinda" });
</script>
