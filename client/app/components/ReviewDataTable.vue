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
import { ref, computed, type PropType } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useToast } from "@/components/ui/toast";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
	Eye,
	Plus,
	Download,
	MoreHorizontal,
	RefreshCcw,
} from "lucide-vue-next";
import {
	getCoreRowModel,
	useVueTable,
	FlexRender,
	type ColumnDef,
} from "@tanstack/vue-table";
import {
	TableActionsAdr,
	TableActionsCausalityAssessmentLevel,
} from "#components";

// Types
interface Review {
	id: string;
	user_id: string;
	causality_assessment_level?: CausalityAssessmentLevelEnum;
	approved: boolean;
	proposed_causality_level?: CausalityAssessmentLevelEnum;
	reason?: string;
	created_at: string;
	updated_at: string;
}

// Props
const props = defineProps<{
	data?: Review[];
	isLoading: boolean;
	currentPage: number;
	pageSize: number;
	totalCount: number;
}>();

// Fetch ADR Data

console.log(props.data);
// Table creation
const tableData = computed(() => props.data ?? []);
const numOfPagesOptions = ["10", "20", "50"];

const columns: ColumnDef<Review>[] = [
	{
		id: "user.first_name",
		accessorKey: "user.first_name",
		header: "First Name",
		cell: ({ row }) => h("div", {}, row.getValue("user.first_name")),
		enableSorting: false,
	},
	{
		id: "user.last_name",
		accessorKey: "user.last_name",
		header: "Last Name",
		cell: ({ row }) => h("div", {}, row.getValue("user.last_name")),
		enableSorting: false,
	},

	{
		id: "approved",
		accessorKey: "approved",
		header: "Approved",
		cell: ({ row }) => h("div", {}, row.getValue("approved")),
		enableSorting: false,
	},
	{
		id: "reason",
		accessorKey: "reason",
		header: "Reason",
		cell: ({ row }) => h("div", {}, row.getValue("reason")),
		enableSorting: false,
	},
	{
		id: "proposed_causality_level",
		accessorKey: "proposed_causality_level",
		header: "Proposed Causality Level",
		cell: ({ row }) =>
			h("div", {}, row.getValue("proposed_causality_level")),
		enableSorting: false,
	},

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
