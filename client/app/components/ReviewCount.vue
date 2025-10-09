<template>
	<UCard :class="cardBackgroundClass">
		<template #header>
			<div>
				<p class="text-lg font-semibold">Approved Count</p>
				<p class="text-sm text-gray-500">The tally of votes</p>
			</div>
		</template>

		<div class="flex w-max mx-auto items-center">
			<div class="text-center">
				<p>Approved</p>
				<p class="text-6xl p-4 font-bold">{{ props.approvedCount }}</p>
			</div>

			<USeparator orientation="vertical" class="mx-6 h-16" />

			<div class="text-center">
				<p>Not Approved</p>
				<p class="text-6xl p-4 font-bold">{{ props.notApprovedCount }}</p>
			</div>
		</div>
	</UCard>
</template>

<script setup lang="ts">
const props = defineProps<{
	approvedCount: number
	notApprovedCount: number
}>()

const isApproved = computed<"yes" | "no" | "tie">(() => {
	if (props.approvedCount > props.notApprovedCount) return "yes"
	if (props.approvedCount < props.notApprovedCount) return "no"
	return "tie"
})

const cardBackgroundClass = computed(() => {
	switch (isApproved.value) {
		case "yes":
			return "bg-green-50"
		case "no":
			return "bg-red-50"
		case "tie":
			return "bg-yellow-50"
		default:
			return ""
	}
})
</script>


<style lang="css" scoped>
@reference "assets/css/main.css";

.big-number {
	@apply text-6xl p-4;
}
</style>
