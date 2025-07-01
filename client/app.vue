<template>
	<ClientOnly>
		<Toaster />
	</ClientOnly>
	<div>
		<NuxtLayout>
			<NuxtPage />
		</NuxtLayout>

		<!-- <NuxtPage /> -->
	</div>
</template>

<script setup lang="ts">
useHead({
	meta: [
		{
			name: "viewport",
			content: "width=device-width, initial-scale=1.0",
		},
	],
});
</script>

<style lang="css">
* {
	font-family: "Inter";
}

/* This targets dark mode */
@media (prefers-color-scheme: dark) {
	/* Change the color of the SVG icon to white */
	img[src*="favicon.svg"] {
		filter: invert(100%) brightness(100%);
	}
}

/* This targets light mode */
@media (prefers-color-scheme: light) {
	/* Change the color of the SVG icon to black */
	img[src*="favicon.svg"] {
		filter: invert(0%) brightness(100%);
	}
}
html {
	scroll-behavior: smooth;
}
.page-responsive-width {
	@apply px-8 lg:px-32;
}

.page-wrapper {
	@apply page-responsive-width py-8;
}

.page-title {
	@apply text-2xl font-bold mb-6;
}

.form-section {
}

.form-section-header {
	@apply font-semibold text-lg scroll-mt-24 my-4;
}

.form-field-wrapper {
	@apply my-8;
}

.view-details-wrapper {
	@apply flex justify-between;
}

.view-details-header {

}

.view-details-content {
	@apply bg-accent rounded-sm px-2
}
/* Transitions  */
.v-enter-active,
.v-leave-active {
	transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
	opacity: 0;
}

.badge {
	@apply text-xs font-bold py-1 px-2 rounded-md w-max;
}

.form-section-header-icon {
	@apply w-6 h-6 text-gray-300;
}

.blank-badge {
	@apply bg-zinc-100 text-gray-400 outline-dashed outline-2 outline-gray-400;
}


</style>
