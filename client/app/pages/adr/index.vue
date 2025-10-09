<template>
	<div class="page-wrapper">
		<p class="page-title">ADR Management</p>
		<NuxtLink to="/adr/add" class="text-white">
			<UButton class="w-full my-4 justify-center"> Add Adr </UButton>
		</NuxtLink>

		<UTable
			ref="table"
			:data="rows"
			:columns="columns"
			class="flex-1"
			:loading="isPending"
		/>
		<UPagination
			:total="totalCount"
			:items-per-page="pageSize"
			:default-page="currentPage"
			show-edges
			color="neutral"
			@update:page="(p) => (currentPage = p)"
		/>
	</div>
</template>

<script setup lang="ts">
import { fetchAdrsWithCausalityAndReviewCount } from "@/api/adr";
import type { ADRWithCausalityLevelAndReviewCountInterface } from "@/types/adr";
import type { PaginatedResponseInterface } from "@/types/pagination";
import type { TableColumn } from "@nuxt/ui";
import { useQuery } from "@tanstack/vue-query";
import type { Row } from "@tanstack/vue-table";
import { capitalize } from "lodash";

// const filterInputRef = ref<HTMLInputElement | null>(null);
const UBadge = resolveComponent("UBadge");
const UIcon = resolveComponent("UIcon");
const UDropdownMenu = resolveComponent("UDropdownMenu");
const UButton = resolveComponent("UButton");

const table = useTemplateRef("table");
const currentPage = ref(1);
const pageSize = ref(20);
const tableFilter = ref<string>("");
const debouncedTableFilter = refDebounced(tableFilter, 1000);

const { data, isPending, isError, error, status } = useQuery<
	PaginatedResponseInterface<ADRWithCausalityLevelAndReviewCountInterface>
>({
	queryKey: ["adrs", currentPage, pageSize, debouncedTableFilter],
	queryFn: () =>
		fetchAdrsWithCausalityAndReviewCount({
			page: currentPage.value,
			size: pageSize.value,
			query: debouncedTableFilter.value,
		}),
});

console.log(data.value);

const totalCount = computed(() => data.value?.total ?? 0);

const rows = computed<ADRWithCausalityLevelAndReviewCountInterface[]>(
	() => data.value?.items ?? []
);

const columns: TableColumn<ADRWithCausalityLevelAndReviewCountInterface>[] = [
	{
		accessorKey: "patient_name",
		header: "Patient Name",
	},
	{
		accessorKey: "causality_assessment_level_value",
		header: "Causality Assessment Level Value",
		cell: ({ row }) => {
			const value: string = row.getValue(
				"causality_assessment_level_value"
			) as string;
			const colorMap: Record<string, string> = {
				certain: "bg-red-500 text-white",
				likely: "bg-red-400 text-black",
				possible: "bg-yellow-500 text-black",
				unlikely: "bg-yellow-300 text-black",
				unclassified: "bg-slate-500 text-white",
				unclassifiable: "bg-slate-300 text-black",
			};
			const color = colorMap[value] || "gray";

			return h(UBadge, { class: `${color}` }, () =>
				capitalize(row.getValue("causality_assessment_level_value"))
			);
		},
	},

	{
		id: "review_count",
		header: "Reviews (Approved | Not Approved)",
		cell: ({ row }) => {
			const approved = row.original.approved_reviews as number;
			const unapproved = row.original.unapproved_reviews as number;

			let iconName = "i-lucide-minus";
			let iconColor = "text-yellow-600";

			if (approved > unapproved) {
				iconName = "i-lucide-check";
				iconColor = "text-green-600";
			} else if (approved < unapproved) {
				iconName = "i-lucide-x";
				iconColor = "text-red-600";
			}

			return h("div", { class: "flex items-center gap-2" }, [
				h(UIcon, { name: iconName, class: `w-5 h-5 ${iconColor}` }),
				h("span", {}, `${approved} | ${unapproved}`),
			]);
		},
	},
	{
		accessorKey: "created_by",
		header: "Created By",
	},
	{
		accessorKey: "created_at",
		header: "Created At",
		cell: ({ row }) =>
			`${row.original.created_at.slice(0, 10)} ${formatTime(
				row.original.created_at
			)}`,
	},
	{
		id: "actions",

		cell: ({ row }) => {
			return h(
				"div",
				{ class: "text-right" },
				h(
					UDropdownMenu,
					{
						content: {
							align: "end",
						},
						items: getRowItems(row),
						"aria-label": "Actions dropdown",
					},
					() =>
						h(UButton, {
							icon: "i-lucide-ellipsis-vertical",
							color: "neutral",
							variant: "ghost",
							class: "ml-auto",
							"aria-label": "Actions dropdown",
						})
				)
			);
		},
	},
];

function getRowItems(row: Row<ADRWithCausalityLevelAndReviewCountInterface>) {
	return [
		{
			type: "label",
			label: "Actions",
		},
		{
			label: "View",
			onSelect() {
				navigateTo(`/adr/${row.original.adr_id}`);
				console.log("navigate to ", row.original.adr_id);
			},
		},
		// {
		// 	type: "separator",
		// },
		// {
		// 	label: "View customer",
		// },
		// {
		// 	label: "View payment details",
		// },
	];
}

function formatTime(isoString: string): string {
	const date = new Date(isoString);
	return new Intl.DateTimeFormat("en-US", {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	}).format(date);
}

useHead({ title: "ADR | MediLinda" });
</script>
