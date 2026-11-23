<template>
	<div class="flex justify-center py-8">
		<NuxtLink :to="aboutPath" aria-label="Read about MediLinda"><Logo /></NuxtLink>
	</div>
	<slot />
</template>

<script setup lang="ts">
import { ABOUT_PATH } from "~/utils/route-access";

const aboutPath = ABOUT_PATH;
</script>
