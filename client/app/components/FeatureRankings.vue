<!-- <template>
	<Card class="my-4">
		<CardHeader>
			<CardTitle> Feature Rankings Per Class using SHAP </CardTitle>
			<CardDescription>
				Feature Rankings Per Class using SHAP
			</CardDescription>
		</CardHeader>
		<CardContent>
			<Tabs :default-value="featureRankingsPerClassDefaultTab">
				<TabsList>
					<TabsTrigger
						v-for="(classRanking, index) in classRankings"
						:value="classRanking.label || ''"
					>
						{{ `${index + 1}. ${capitalize(classRanking.label)}` }}
					</TabsTrigger>
				</TabsList>
				<TabsContent
					v-for="featureRankingPerClass in featureRankingsPerClass"
					:value="featureRankingPerClass.classLabel || ''"
				>
					<Table>
						<TableCaption>
							Feature Rankings Per Class using SHAP for
							{{ capitalize(featureRankingPerClass.classLabel) }}
						</TableCaption>
						<TableHeader>
							<TableRow>
								<TableHead>Rank</TableHead>
								<TableHead>Feature Name</TableHead>
								<TableHead>Feature Value</TableHead>
								<TableHead>SHAP Value</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							<TableRow
								v-for="(
									feature, index
								) in featureRankingPerClass.features"
							>
								<TableCell>{{ index + 1 }}</TableCell>
								<TableCell>
									{{ useFeatureNameFormatter(feature.name) }}
								</TableCell>
								<TableCell
									v-if="typeof feature.value == 'boolean'"
								>
									<Icon
										v-if="feature.value"
										name="lucide:check"
										class="w-6 h-6 bg-green-500"
									/>
									<Icon
										v-if="!feature.value"
										name="lucide:x"
										class="w-6 h-6 bg-red-500"
									/>
								</TableCell>
								<TableCell
									v-if="typeof feature.value != 'boolean'"
								>
									{{ feature.value }}
								</TableCell>
								
								<TableCell>
									<div class="flex items-center">
										{{
											`${feature.shapValue.toFixed(4)} %`
										}}
										<span
											v-if="feature.shapValue > 0"
											class="text-green-600"
										>
											<Icon
												name="lucide:arrow-up"
												class="w-4 h-4"
											/>
										</span>
										<span
											v-if="feature.shapValue < 0"
											class="text-red-600"
										>
											<Icon
												name="lucide:arrow-down"
												class="w-4 h-4"
											/>
										</span>
										<span
											v-if="feature.shapValue == 0"
											class="text-gray-600"
										>
											<Icon
												name="lucide:minus"
												class="w-4 h-4"
											/>
										</span>
									</div>
								</TableCell>
							</TableRow>
						</TableBody>
					</Table>
				</TabsContent>
			</Tabs>
		</CardContent>
	</Card>
</template> -->

<!--<template>
	 <Card class="my-4">
		<CardHeader>
			<CardTitle> Feature Rankings Per Class using SHAP </CardTitle>
			<CardDescription>
				Feature Rankings Per Class using SHAP
			</CardDescription>
		</CardHeader>
		<CardContent>
			<Tabs :default-value="featureRankingsPerClassDefaultTab">
				<TabsList>
					<TabsTrigger
						v-for="(classRanking, index) in classRankings"
						:value="classRanking.label || ''"
					>
						{{ `${index + 1}. ${capitalize(classRanking.label)}` }}
					</TabsTrigger>
				</TabsList>
				<TabsContent
					v-for="featureRankingPerClass in featureRankingsPerClass"
					:value="featureRankingPerClass.classLabel || ''"
				>
					<Table>
						<TableCaption>
							Feature Rankings Per Class using SHAP for
							{{ capitalize(featureRankingPerClass.classLabel) }}
						</TableCaption>
						<TableHeader>
							<TableRow>
								<TableHead>Rank</TableHead>
								<TableHead>Feature Name</TableHead>
								<TableHead>SHAP Value</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							<TableRow
								v-for="(
									feature, index
								) in featureRankingPerClass.features"
							>
								<TableCell>{{ index + 1 }}</TableCell>
								<TableCell>
									{{ useFeatureNameFormatter(feature.name) }}
								</TableCell>
								<TableCell>
									<div class="flex items-center">
										{{
											`${feature.shapValue.toFixed(4)} %`
										}}
										<span
											v-if="feature.shapValue > 0"
											class="text-green-600"
										>
											<Icon
												name="lucide:arrow-up"
												class="w-4 h-4"
											/>
										</span>
										<span
											v-if="feature.shapValue < 0"
											class="text-red-600"
										>
											<Icon
												name="lucide:arrow-down"
												class="w-4 h-4"
											/>
										</span>
										<span
											v-if="feature.shapValue == 0"
											class="text-gray-600"
										>
											<Icon
												name="lucide:minus"
												class="w-4 h-4"
											/>
										</span>
									</div>
								</TableCell>
							</TableRow>
						</TableBody>
					</Table>
				</TabsContent>
			</Tabs>
		</CardContent>
	</Card> 
</template> -->

<!-- <script setup lang="ts">
// import { capitalize } from "lodash-es";
// import type { ClassRanking } from "@/types/class_ranking";
// const props = defineProps<{
// 	baseValues?: number[];
// 	shapValues?: number[];
// 	baseShapValues?: number[];
// 	shapMatrix?: number[][];
// 	featureNames?: string[];
// 	featureValues?: any[];
// }>();

// const classRankings = computed<ClassRanking[]>(() => {
// 	const baseValues = props.baseValues;
// 	const shapValues = props.shapValues;
// 	const baseShapValues = props.baseShapValues;

// 	if (!baseValues || !shapValues || !baseShapValues) return [];

// 	const rankings: ClassRanking[] = baseValues.map((baseValue, i) => ({
// 		label: useClassLabelFromNumber(i),
// 		baseValue: baseValue * 100,
// 		shapValue: (shapValues[i] ?? 0) * 100,
// 		baseShapValue: (baseShapValues[i] ?? 0) * 100,
// 	}));

// 	return rankings.sort((a, b) => b.baseShapValue - a.baseShapValue);
// });

// const DEFAULT_TAB = "certain";
// const featureRankingsPerClassDefaultTab = computed(() => {
// 	// return classRankings.value[0].label;
// 	// return classRankings.value.length > 0 ? classRankings.value[0].label : "";
// 	return classRankings.value.length > 0
// 		? classRankings.value[0].label
// 		: DEFAULT_TAB;
// });

// const featureRankingsPerClass = computed(() => {
// 	if (
// 		props.baseValues &&
// 		props.shapValues &&
// 		props.baseShapValues &&
// 		props.shapMatrix &&
// 		props.featureNames &&
// 		props.featureValues
// 	) {
// 		const numClasses = props.baseValues.length || 6;
// 		const numFeatures = props.shapMatrix.length;

// 		const result = [];

// 		for (let classIndex = 0; classIndex < numClasses; classIndex++) {
// 			const featuresForClass = [];

// 			for (
// 				let featureIndex = 0;
// 				featureIndex < numFeatures;
// 				featureIndex++
// 			) {
// 				featuresForClass.push({
// 					name: props.featureNames[featureIndex],
// 					value: props.featureValues[featureIndex],
// 					shapValue: props.shapMatrix[featureIndex][classIndex] * 100,
// 				});
// 			}

// 			// Sort by absolute SHAP value (optional, for top contributors)
// 			featuresForClass.sort((a, b) => b.shapValue - a.shapValue);

// 			result.push({
// 				classLabel: useClassLabelFromNumber(classIndex),
// 				features: featuresForClass,
// 			});
// 		}

// 		return result;
// 	}
// 	return [];
// });
</script>
 -->

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
			<UTabs :v-model="defaultTabKey" :items="tabItems" color="neutral">
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

// This now includes a 'key' for the default-value prop
const tabItems = computed<TabsItem[]>(() =>
	featureRankingsPerClass.value.map((ranking) => ({
		// key: ranking.classLabel, // <-- Add a key
		label: capitalize(ranking.classLabel),
		slot: ranking.classLabel,
	}))
);

// --- 💡 CHANGED ---
// We just need to tell UTabs which tab to open by default.
// The `default-value` prop uses the 'key' of the item.
const defaultTabKey = computed(() => {
	return props.defaultClass || tabItems.value[0]?.slot;
});
</script>
