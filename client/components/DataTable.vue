<template>
	<p class="font-bold text-lg">{{ props.title }}</p>
	<div class="flex items-center justify-between content-end py-4">
		<div v-if="$slots.selectionActions" class="flex items-center space-x-2">
			<slot
				name="selectionActions"
				:allSelected="table.getIsAllPageRowsSelected()"
				:someSelected="table.getIsSomePageRowsSelected()"
				:selectedRows="table.getSelectedRowModel().rows"
			></slot>
		</div>
		<Select v-model="selectedPageSize">
			<SelectTrigger class="w-max">
				<SelectValue placeholder="Show number of pages" />
			</SelectTrigger>
			<SelectContent>
				<SelectGroup>
					<SelectItem
						v-for="pageOption in props.numOfPagesOptions"
						:key="pageOption"
						:value="pageOption"
					>
						Show {{ pageOption }} rows
					</SelectItem>
				</SelectGroup>
			</SelectContent>
		</Select>
	</div>

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

<script setup lang="ts" generic="T">
import {
	FlexRender,
	getCoreRowModel,
	useVueTable,
	type ColumnDef,
} from "@tanstack/vue-table";

// Props
const props = withDefaults(
	defineProps<{
		data?: T[];
		columns: ColumnDef<T>[];
		numOfPagesOptions?: string[];
		title?: string;
		currentPage: number;
		pageSize: number;
		totalCount: number;
	}>(),
	{
		title: "Table",
		numOfPagesOptions: () => ["10", "20", "50"],
	}
);

// Table creation
const tableData = computed(() => props.data ?? []);

const table = useVueTable({
	get data() {
		return tableData.value;
	},
	columns: props.columns,
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

// }
</script>
