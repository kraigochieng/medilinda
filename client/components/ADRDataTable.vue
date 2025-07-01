<template>
	<div class="flex items-center justify-between content-end py-4">
		<p>ADR Management</p>
		<Select v-model="selectedPageSize">
			<SelectTrigger class="w-max">
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
	</div>

	<Table class="rounded-md border">
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
				<template v-for="row in table.getRowModel().rows" :key="row.id">
					<TableRow :data-state="row.getIsSelected() && 'selected'">
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
				<TableCell :colspan="columns.length" class="h-24 text-center">
					No results.
				</TableCell>
			</TableRow>
		</TableBody>
	</Table>
	<Pagination
		v-slot="{ page }"
		:items-per-page="pageSize"
		:total="totalCount"
		:sibling-count="1"
		show-edges
		:default-page="1"
		class="py-4 w-max m-auto"
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
</template>

<script setup lang="ts">
import { TableActionsAdr } from "#components";
import {
	FlexRender,
	getCoreRowModel,
	useVueTable,
	type ColumnDef,
} from "@tanstack/vue-table";
import Checkbox from "./ui/checkbox/Checkbox.vue";

const numOfPagesOptions = ["10", "20", "50"];

interface ADRReviewFull {
	id: string;
	patient_id: string;
	user_id: string;
	gender: string;
	pregnancy_status: string;
	known_allergy: string;
	rechallenge: string;
	dechallenge: string;
	severity: string;
	is_serious: string;
	criteria_for_seriousness: string;
	action_taken: string;
	outcome: string;
	created_at: string;
	updated_at: string;
	causality_assessment_levels?: ADRCausality[]; // Array of reviews
}

interface ADRCausality {
	id: string;
	adr_id: string;
	ml_model_id: string;
	causality_assessment_level_value: CausalityAssessmentLevelEnum;
	created_at: string;
	updated_at: string;
	reviews: ADRReview[];
}

// Define the ADR & Review interfaces
interface ADRReview {
	id: string;
	causality_assessment_level_id: string;
	user_id: string;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string | null;
	created_at: string;
	updated_at: string;
}

// Props
const props = defineProps<{
	data?: ADRReviewFull[];
	isLoading: boolean;
	currentPage: number;
	pageSize: number;
	totalCount: number;
}>();

// Table creation
const tableData = computed(() => props.data ?? []);

const columns: ColumnDef<ADRReviewFull>[] = [
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
		id: "patient_id",
		accessorKey: "patient_id",
		header: "Patient ID",
		cell: ({ row }) => h("div", {}, row.getValue("patient_id")),
		enableSorting: false,
	},
	{
		id: "gender",
		accessorKey: "gender",
		header: "Gender",
		cell: ({ row }) => h("div", {}, row.getValue("gender")),
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
			return h(TableActionsAdr, {
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
	// data: tableData.value
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

// function handlePageSizeChange(event: Event) {

// 	const selectedPageSize = (event.target as HTMLSelectElement).value;
// 	emit("pageSizeChange", Number(selectedPageSize)); // Emit the selected page size to the parent
// 	console.log("page size changed")
// }
</script>
