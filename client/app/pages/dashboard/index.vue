<template>
	<div class="page-wrapper space-y-6">
		<div class="flex items-center justify-between gap-4">
			<h1 class="text-2xl font-bold">Dashboard</h1>
			<UButton
				color="neutral"
				variant="outline"
				icon="i-lucide-printer"
				label="Print"
				class="print:hidden"
				@click="print"
			/>
		</div>

		<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
			<GraphReviewedVSUnreviewed />
			<GraphCausalityDistribution />
			<GraphApprovalStatus />
			<GraphTopInstitutions />
		</div>
	</div>
</template>

<script setup lang="ts">
function print() {
	window.print();
}

useHead({ title: "Dashboard | MediLinda" });
</script>
