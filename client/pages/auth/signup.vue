<template>
	<form @submit.prevent="onSubmit" class="my-16 mx-auto w-96">
		<Card>
			<CardHeader><CardTitle>Sign Up</CardTitle></CardHeader>
			<CardContent>
				<FormInput
					type="text"
					name="firstName"
					label="First Name"
					placeholder="Enter First Name"
				/>
				<FormInput
					type="text"
					name="lastName"
					label="Last Name"
					placeholder="Enter Last Name"
				/>
				<FormInput
					type="text"
					name="username"
					label="Username"
					placeholder="Enter Username"
				/>
				<FormInput
					type="password"
					name="password"
					label="Password"
					placeholder="Enter Password"
				/>

				<p v-show="authStore.isSignupError">Signup Error</p>
			</CardContent>
			<CardFooter class="flex justify-between px-6 pb-6">
				<Button type="submit">Sign Up</Button>
				<Button variant="ghost">
					<NuxtLink to="/auth/login"
						>Already have an account?</NuxtLink
					>
				</Button>
			</CardFooter>
		</Card>
	</form>
</template>

<script setup lang="ts">
import FormInput from "@/components/ui/custom/FormInput.vue";

const authStore = useAuthStore();

const { values, errors, defineField, handleSubmit, isSubmitting } = useForm({
	validationSchema: toTypedSchema(signupValidationSchema),
});

const [username, usernameAttrs] = defineField("username");
const [password, passwordAttrs] = defineField("password");
const [firstName, firstNameAttrs] = defineField("firstName");
const [lastName, lastNameAttrs] = defineField("lastName");

const onSubmit = handleSubmit((values) => {
	authStore.signup(values);
});

definePageMeta({
	layout: "auth",
});

useHead({ title: "Signup | MediLinda" });
</script>
