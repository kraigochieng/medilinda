<template>
	<UCard class="my-4" v-if="featureRankingsPerClass.length > 0">
		<template #header>
			<h3
				class="text-base font-semibold leading-6 text-gray-900 dark:text-white"
			>
				Feature Contribution Rankings (SHAP)
			</h3>
			<p class="mt-1 text-sm text-gray-500">
				How each feature contributed to the likelihood of each outcome.
				Features are ranked by their impact.
			</p>
		</template>

		<template #default>
			<UTabs :default-value="defaultTabKey" :items="tabItems" color="neutral">
				<template
					v-for="ranking in featureRankingsPerClass"
					#[ranking.classLabel]
					:key="ranking.classLabel"
				>
					<UTable
						:data="ranking.features"
						:columns="tableColumns"
						class="mt-4"
					/>
				</template>
			</UTabs>
		</template>
	</UCard>

	<UCard class="my-4" v-else>
		<template #header>
			<h3
				class="text-base font-semibold leading-6 text-gray-900 dark:text-white"
			>
				Feature Contribution Rankings (SHAP)
			</h3>
		</template>
		<p class="text-sm text-gray-500">
			No feature ranking data is available for this causality assessment.
		</p>
	</UCard>
</template>

<script setup lang="ts">
import type { TableColumn, TabsItem } from "@nuxt/ui";
import { capitalize } from "lodash-es";
import { computed, h, resolveComponent } from "vue";

const UBadge = resolveComponent("UBadge");
const UIcon = resolveComponent("UIcon");

interface FeatureRanking {
	rank: number;
	name: string;
	value: any;
	shapValue: number;
}

const props = defineProps<{
	defaultClass?: string;
	shapMatrix?: number[][];
	featureNames?: string[];
	featureValues?: any[];
	baseValues?: number[];
}>();

// This definition for columns is perfect and doesn't need to change.
const tableColumns: TableColumn<FeatureRanking>[] = [
	{
		accessorKey: "rank",
		header: "Rank",
	},
	{
		accessorKey: "name",
		header: "Feature Name",
		cell: ({ row }) => {
			const name = row.getValue("name") as string;
			return useFeatureNameFormatter(name);
		},
	},
	{
		accessorKey: "value",
		header: "Feature Value",
		cell: ({ row }) => {
			const value = row.getValue("value");
			if (typeof value === "boolean") {
				return h(UIcon, {
					name: value
						? "i-heroicons-check-circle"
						: "i-heroicons-x-circle",
					class: value
						? "w-6 h-6 text-green-500"
						: "w-6 h-6 text-red-500",
				});
			}
			if (value === null || value === undefined) {
				return h(
					UBadge,
					{ color: "gray", variant: "soft" },
					() => "BLANK"
				);
			}
			return h("span", {}, `${value}`);
		},
	},
	{
		accessorKey: "shapValue",
		header: "SHAP Value (Contribution)",
		cell: ({ row }) => {
			const value = row.getValue("shapValue") as number;
			let colorClass = "text-gray-500 dark:text-gray-400";
			let iconName = "i-heroicons-minus";
			if (value > 0.0001) {
				colorClass = "text-green-600 dark:text-green-400";
				iconName = "i-heroicons-arrow-up";
			} else if (value < -0.0001) {
				colorClass = "text-red-600 dark:text-red-400";
				iconName = "i-heroicons-arrow-down";
			}
			return h(
				"div",
				{ class: `flex items-center font-medium ${colorClass}` },
				[
					h("span", {}, `${(value * 100).toFixed(2)} %`),
					h(UIcon, { name: iconName, class: "w-4 h-4 ml-1" }),
				]
			);
		},
	},
];

// This computed prop is perfect and stays the same.
const featureRankingsPerClass = computed(() => {
	const { baseValues, shapMatrix, featureNames, featureValues } = props;
	if (!baseValues || !shapMatrix || !featureNames || !featureValues) {
		return [];
	}
	if (
		featureNames.length !== featureValues.length ||
		featureNames.length !== shapMatrix.length
	) {
		console.error("SHAP data mismatch: Array lengths do not match.");
		return [];
	}
	try {
		const numClasses = baseValues.length;
		const numFeatures = featureNames.length;
		const result = [];
		for (let classIndex = 0; classIndex < numClasses; classIndex++) {
			const featuresForClass = [];
			for (
				let featureIndex = 0;
				featureIndex < numFeatures;
				featureIndex++
			) {
				const shapRow = shapMatrix[featureIndex];
				if (shapRow) {
					featuresForClass.push({
						name: featureNames[featureIndex],
						value: featureValues[featureIndex],
						shapValue: shapRow[classIndex],
					});
				}
			}
			featuresForClass.sort(
				(a, b) =>
					Math.abs(b.shapValue as number) -
					Math.abs(a.shapValue as number)
			);
			result.push({
				classLabel: useClassLabelFromNumber(classIndex),
				features: featuresForClass.map(
					(f, index) =>
						({
							...f,
							rank: index + 1,
						} as FeatureRanking)
				),
			});
		}
		return result;
	} catch (error) {
		console.error("Error computing feature rankings:", error);
		return [];
	}
});

const tabItems = computed<TabsItem[]>(() =>
	featureRankingsPerClass.value.map((ranking) => ({
		label: capitalize(ranking.classLabel),
		value: ranking.classLabel,
		slot: ranking.classLabel,
	}))
);

// Open the tab of the predicted class, or the first one.
const defaultTabKey = computed(() => {
	const predicted = tabItems.value.find((item) => item.value === props.defaultClass);
	return (predicted ?? tabItems.value[0])?.value;
});
</script>
