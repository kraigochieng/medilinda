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

<template>
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
</template>

<script setup lang="ts">
import { capitalize } from "lodash";

const props = defineProps<{
	baseValues?: number[];
	shapValues?: number[];
	baseShapValues?: number[];
	shapMatrix?: number[][];
	featureNames?: string[];
	featureValues?: any[];
}>();

const classRankings = computed<ClassRanking[]>(() => {
	if (props.baseValues && props.shapValues && props.baseShapValues) {
		const rankings = [];
		for (let i = 0; i < props.baseValues.length; i++) {
			rankings.push({
				label: useClassLabelFromNumber(i),
				baseValue: props.baseValues[i] * 100,
				shapValue: props.shapValues[i] * 100,
				baseShapValue: props.baseShapValues[i] * 100,
			});
		}

		return rankings.sort((a, b) => b.baseShapValue - a.baseShapValue);
	}
	return [];
});

const DEFAULT_TAB = "certain";
const featureRankingsPerClassDefaultTab = computed(() => {
	// return classRankings.value[0].label;
	// return classRankings.value.length > 0 ? classRankings.value[0].label : "";
	return classRankings.value.length > 0
		? classRankings.value[0].label
		: DEFAULT_TAB;
});

const featureRankingsPerClass = computed(() => {
	if (
		props.baseValues &&
		props.shapValues &&
		props.baseShapValues &&
		props.shapMatrix &&
		props.featureNames &&
		props.featureValues
	) {
		const numClasses = props.baseValues.length || 6;
		const numFeatures = props.shapMatrix.length;

		const result = [];

		for (let classIndex = 0; classIndex < numClasses; classIndex++) {
			const featuresForClass = [];

			for (
				let featureIndex = 0;
				featureIndex < numFeatures;
				featureIndex++
			) {
				featuresForClass.push({
					name: props.featureNames[featureIndex],
					value: props.featureValues[featureIndex],
					shapValue: props.shapMatrix[featureIndex][classIndex] * 100,
				});
			}

			// Sort by absolute SHAP value (optional, for top contributors)
			featuresForClass.sort((a, b) => b.shapValue - a.shapValue);

			result.push({
				classLabel: useClassLabelFromNumber(classIndex),
				features: featuresForClass,
			});
		}

		return result;
	}
	return [];
});
</script>
