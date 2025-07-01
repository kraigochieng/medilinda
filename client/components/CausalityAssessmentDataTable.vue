<template>
	<div class="rounded-md border">
		<Table>
			<TableHeader>
				<TableRow
					v-for="headerGroup in table.getHeaderGroups()"
					:key="headerGroup.id"
				>
					<TableHead
						v-for="header in headerGroup.headers"
						:key="header.id"
					>
						<FlexRender
							v-if="!header.isPlaceholder"
							:render="header.column.columnDef.header"
							:props="header.getContext()"
						/>
					</TableHead>
				</TableRow>
			</TableHeader>
			<TableBody>
				<template v-if="table.getRowModel().rows?.length">
					<template
						v-for="row in table.getRowModel().rows"
						:key="row.id"
					>
						<TableRow
							:data-state="row.getIsSelected() && 'selected'"
						>
							<TableCell
								v-for="cell in row.getVisibleCells()"
								:key="cell.id"
							>
								<FlexRender
									:render="cell.column.columnDef.cell"
									:props="cell.getContext()"
								/>
							</TableCell>
						</TableRow>
						<TableRow v-if="row.getIsExpanded()">
							<TableCell :colspan="row.getAllCells().length">
								{{ JSON.stringify(row.original) }}
							</TableCell>
						</TableRow>
					</template>
				</template>

				<TableRow v-else>
					<TableCell
						:colspan="columns.length"
						class="h-24 text-center"
					>
						No results.
					</TableCell>
				</TableRow>
			</TableBody>
		</Table>
	</div>
	<Pagination
		v-slot="{ page }"
		:items-per-page="pageSize"
		:total="totalCount"
		:sibling-count="1"
		show-edges
		:default-page="1"
	>
		<PaginationList v-slot="{ items }" class="flex items-center gap-1">
			<PaginationFirst />
			<PaginationPrev />

			<template v-for="(item, index) in items">
				<PaginationListItem
					v-if="item.type === 'page'"
					:key="index"
					:value="item.value"
					as-child
				>
					<Button
						class="w-9 h-9 p-0"
						:variant="item.value === page ? 'default' : 'outline'"
						@mouseup="handlePageChange(item.value)"
					>
						{{ item.value }}
					</Button>
				</PaginationListItem>
				<PaginationEllipsis v-else :key="item.type" :index="index" />
			</template>

			<PaginationNext />
			<PaginationLast />
		</PaginationList>
	</Pagination>
	<Select v-model="selectedPageSize">
		<SelectTrigger>
			<SelectValue placeholder="Show number of pages" />
		</SelectTrigger>
		<SelectContent>
			<SelectGroup>
				<SelectItem
					v-for="pageOption in numOfPagesOptions"
					:key="pageOption"
					:value="pageOption"
				>
					Show {{ pageOption }} rows
				</SelectItem>
			</SelectGroup>
		</SelectContent>
	</Select>
</template>

<script setup lang="ts">
// Imports
import {
	FlexRender,
	getCoreRowModel,
	useVueTable,
	type ColumnDef,
} from "@tanstack/vue-table";
import { computed, ref } from "vue";

import TableActionsCausalityAssessmentLevel from "@/components/table/actions/CausalityAssessmentLevel.vue";

import Checkbox from "./ui/checkbox/Checkbox.vue";

// Types
interface ADRCausality {
	id: string;
	adr_id: string;
	ml_model_id: string;
	causality_assessment_level_value: CausalityAssessmentLevelEnum;
	created_at: string;
	updated_at: string;
}
// Props
const props = defineProps<{
	data?: ADRCausality[];
	isLoading: boolean;
	currentPage: number;
	pageSize: number;
	totalCount: number;
}>();

console.log(props.data);
// Table creation
const tableData = computed(() => props.data ?? []);
const numOfPagesOptions = ["10", "20", "50"];

const columns: ColumnDef<ADRCausality>[] = [
	{
		id: "select",
		header: ({ table }) =>
			h(Checkbox, {
				modelValue:
					table.getIsAllPageRowsSelected() ||
					(table.getIsSomePageRowsSelected() && "indeterminate"),
				"onUpdate:modelValue": (value) =>
					table.toggleAllPageRowsSelected(!!value),
				ariaLabel: "Select all",
			}),
		cell: ({ row }) =>
			h(Checkbox, {
				modelValue: row.getIsSelected(),
				"onUpdate:modelValue": (value) => row.toggleSelected(!!value),
				ariaLabel: "Select row",
			}),
		enableSorting: false,
		enableHiding: false,
	},
	{
		id: "ml_model_id",
		accessorKey: "ml_model_id",
		header: "ML Model ID",
		cell: ({ row }) => h("div", {}, row.getValue("ml_model_id")),
		enableSorting: false,
	},
	{
		id: "causality_assessment_level_value",
		accessorKey: "causality_assessment_level_value",
		header: "Causality Assessment Level",
		cell: ({ row }) =>
			h("div", {}, row.getValue("causality_assessment_level_value")),
	},
	// {
	// 	accessorKey:
	// 		"causality_assessment_levels.causality_assessment_level_value",
	// 	header: "Causality Assessment Level",
	// 	cell: ({ row }) =>
	// 		h(
	// 			"div",
	// 			{},
	// 			row.getValue(
	// 				"causality_assessment_levels"
	// 			)
	// 		),
	// },
	{
		id: "actions",
		enableHiding: false,
		cell: ({ row }) => {
			return h(TableActionsCausalityAssessmentLevel, {
				row: row.original,
				onExpand: row.toggleExpanded,
			});
		},
	},
];

const table = useVueTable({
	get data() {
		return tableData.value;
	},
	columns: columns,
	getCoreRowModel: getCoreRowModel(),
});

// Emits
const emit = defineEmits<{
	pageChange: [page: number];
	pageSizeChange: [size: number];
}>();

function handlePageChange(page: number) {
	emit("pageChange", page);
}

const selectedPageSize = ref("20"); // Default value

watch(selectedPageSize, (newSize) => {
	emit("pageSizeChange", Number(newSize)); // Emit the new value when it changes
});
</script>
