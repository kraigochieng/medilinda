<template>
	<Card class="my-4">
		<CardHeader>
			<CardTitle>Class Rankings Using SHAP</CardTitle>
			<CardDescription>Uses SHAP values</CardDescription>
		</CardHeader>
		<CardContent>
			<Table>
				<TableCaption> Class Rankings Using SHAP </TableCaption>
				<TableHeader>
					<TableRow>
						<TableHead>Rank</TableHead>
						<TableHead>Label</TableHead>
						<TableHead>Base Value</TableHead>
						<TableHead>SHAP Value</TableHead>
						<TableHead>Base + SHAP Value</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					<TableRow v-for="(item, index) in classRankings">
						<TableCell> {{ index + 1 }}</TableCell>
						<TableCell>{{ capitalize(item.label) }}</TableCell>
						<TableCell>
							{{ `${item.baseValue.toFixed(4)} %` }}
						</TableCell>
						<TableCell>
							<div class="flex items-center gap-2">
								<Icon
									v-if="item.shapValue > 0"
									name="lucide:arrow-up"
									class="w-4 h-4 text-green-600"
								/>

								<Icon
									v-if="item.shapValue < 0"
									name="lucide:arrow-down"
									class="w-4 h-4 text-red-600"
								/>
								<p>{{ `${item.shapValue.toFixed(4)} %` }}</p>
							</div>
						</TableCell>
						<TableCell>
							{{ `${item.baseShapValue.toFixed(4)} %` }}
						</TableCell>
					</TableRow>
				</TableBody>
			</Table>
		</CardContent>
		<CardFooter class="flex justify-end">
			<Dialog>
				<DialogTrigger as-child>
					<Button variant="ghost" class="flex items-center">
						<Icon name="lucide:circle-help" />
						<p>Help</p>
					</Button>
				</DialogTrigger>
				<DialogContent>
					<DialogHeader>
						<DialogTitle> Help </DialogTitle>
						<DialogDescription> Help </DialogDescription>
					</DialogHeader>
					<ul
						class="py-4 text-sm text-neutral-700 dark:text-neutral-400"
					>
						<li><strong>Base Value:</strong> Base Value</li>
						<li><strong>SHAP Value:</strong> SHAP Value</li>
						<li><strong>Base + SHAP Value:</strong> Base + SHAP</li>
					</ul>
				</DialogContent>
			</Dialog>
		</CardFooter>
	</Card>
</template>

<script setup lang="ts">
import type { ClassRanking } from "@/types/class_ranking";
import { capitalize } from "lodash";

const props = defineProps<{
	baseValues?: number[];
	shapValues?: number[];
	baseShapValues?: number[];
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
</script>
