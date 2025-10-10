<template>
	<div class="page-wrapper">
		<FormADR mode="update" :id="id" />
	</div>
</template>

<script setup lang="ts">
const route = useRoute();
const id = route.params.id as string;

useHead({ title: "Edit an ADR | MediLinda" });
</script>
