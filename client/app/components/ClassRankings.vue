<template>
	<UCard>
		<template #header>
			<p>Class Rankings Using SHAP</p>
		</template>
		<template #default>
			<UTable :data="classRankings" :columns="columns" />
		</template>
		<template #footer class="flex justify-end">
			<UModal>
				<UButton label="Help" color="neutral" variant="ghost" />
				<template #content>
					<ul
						class="py-4 text-sm text-neutral-700 dark:text-neutral-400"
					>
						<li><strong>Base Value:</strong> Base Value</li>
						<li><strong>SHAP Value:</strong> SHAP Value</li>
						<li><strong>Base + SHAP Value:</strong> Base + SHAP</li>
					</ul>
				</template>
			</UModal>
		</template>
	</UCard>
</template>

<script setup lang="ts">
import type { ClassRanking } from "@/types/class_ranking";
import type { TableColumn } from "@nuxt/ui";

const props = defineProps<{
	baseValues?: number[];
	shapValues?: number[];
	baseShapValues?: number[];
}>();

const classRankings = computed<ClassRanking[]>(() => {
	const baseValues = props.baseValues;
	const shapValues = props.shapValues;
	const baseShapValues = props.baseShapValues;

	if (!baseValues || !shapValues || !baseShapValues) return [];

	const rankings: ClassRanking[] = baseValues.map((baseValue, i) => ({
		label: useClassLabelFromNumber(i),
		baseValue: baseValue * 100,
		shapValue: (shapValues[i] ?? 0) * 100,
		baseShapValue: (baseShapValues[i] ?? 0) * 100,
	}));

	return rankings.sort((a, b) => b.baseShapValue - a.baseShapValue);
});

const columns: TableColumn<ClassRanking>[] = [
	{
		id: "rank",
		header: "Rank",
		cell: ({row}) => row.index + 1
	},
	{
		accessorKey: "label",
		header: "Label",
	},
	{
		accessorKey: "baseValue",
		header: "Base Value",
		cell: ({ row }) => `${row.original.baseValue.toFixed(4)} %`,
	},
	{
		accessorKey: "shapValue",
		header: "SHAP Value",
		cell: ({ row }) => {
			const shapValue = row.original.shapValue;
			const Icon = resolveComponent("Icon");

			return h("div", { class: "flex items-center gap-2" }, [
				shapValue > 0
					? h(Icon, {
							name: "lucide:arrow-up",
							class: "w-4 h-4 text-green-600",
					  })
					: shapValue < 0
					? h(Icon, {
							name: "lucide:arrow-down",
							class: "w-4 h-4 text-red-600",
					  })
					: null,
				h("p", `${shapValue.toFixed(4)} %`),
			]);
		},
	},
	{
		accessorKey: "baseShapValue",
		header: "Base + SHAP Value",
		cell: ({ row }) => `${row.original.baseShapValue.toFixed(4)} %`,
	},
];
</script>
