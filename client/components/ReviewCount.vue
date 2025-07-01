<template>
	<Card :class="cardBackgroundClass">
		<CardHeader>
			<CardTitle>Approved Count</CardTitle>
			<CardDescription>The tally of votes</CardDescription>
		</CardHeader>
		<CardContent>
			<div class="flex w-max mx-auto">
				<div class="text-center">
					<p>Approved</p>
					<p class="big-number">
						{{ props.approvedCount }}
					</p>
				</div>

				<VerticalSeparator />

				<div class="text-center">
					<p>Not Approved</p>
					<p class="big-number">
						{{ props.notApprovedCount }}
					</p>
				</div>
			</div>
		</CardContent>
	</Card>
</template>

<script setup lang="ts">
const props = defineProps<{
	approvedCount: number;
	notApprovedCount: number;
}>();

const isApproved = computed<"yes" | "no" | "tie">(() => {
	if (props.approvedCount > props.notApprovedCount) {
		return "yes";
	} else if (props.approvedCount < props.notApprovedCount) {
		return "no";
	} else {
		return "tie";
	}
});

const cardBackgroundClass = computed(() => {
	switch (isApproved.value) {
		case "yes":
			return "bg-green-50";
		case "no":
			return "bg-red-50";
		case "tie":
			return "bg-yellow-50";
		default:
			return "";
	}
});
</script>

<style lang="css" scoped>
.big-number {
	@apply text-6xl p-4;
}
</style>
