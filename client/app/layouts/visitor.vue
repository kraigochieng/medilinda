<template>
	<div class="mx-auto flex max-w-3xl items-center justify-between px-4 py-6">
		<NuxtLink to="/" class="flex items-center"><Logo /></NuxtLink>
		<UButton to="/auth/login" label="Sign in" color="neutral" variant="outline" />
	</div>
	<main class="px-4 pb-12">
		<slot />
	</main>
</template>
