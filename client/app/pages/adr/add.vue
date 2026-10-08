<template>
	<div class="page-wrapper">
		<p class="mb-4 text-sm text-muted">
			Fill in the report. Your work is saved as a draft in this browser tab, so a refresh does not lose
			it. Use <strong>Fill sample data</strong> to try the form with an example patient.
		</p>
		<FormADR mode="create" />
	</div>
</template>

<script setup lang="ts">
useHead({ title: "Add ADR | MediLinda" });
</script>
