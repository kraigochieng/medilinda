<template>
	<div class="mx-auto max-w-4xl space-y-8">
		<div class="flex flex-wrap items-center justify-between gap-4">
			<div>
				<h1 class="text-2xl font-bold">{{ title }}</h1>
				<p class="text-muted">Here is where your ADR work stands.</p>
			</div>
			<UButton to="/adr/add" icon="i-lucide-plus" label="Add ADR" size="lg" />
		</div>

		<UAlert
			v-if="isError"
			color="error"
			variant="subtle"
			icon="i-lucide-triangle-alert"
			title="Could not load the counts"
			:actions="[{ label: 'Try again', color: 'neutral', onClick: () => refetchAll() }]"
		/>

		<div class="grid gap-4 sm:grid-cols-3">
			<NuxtLink
				v-for="card in cards"
				:key="card.key"
				:to="card.to"
				class="group block rounded-lg focus-visible:outline-2 focus-visible:outline-primary"
			>
				<UCard class="h-full transition group-hover:bg-elevated">
					<div class="flex items-start justify-between gap-2">
						<div>
							<p class="text-sm font-medium text-muted">{{ card.label }}</p>
							<USkeleton v-if="card.value === undefined && !isError" class="mt-2 h-9 w-16" />
							<p v-else class="mt-1 text-3xl font-bold">{{ card.value ?? "—" }}</p>
						</div>
						<UIcon :name="card.icon" class="size-6 text-muted" />
					</div>
					<p class="mt-2 text-xs text-muted">{{ card.hint }}</p>
				</UCard>
			</NuxtLink>
		</div>

		<p class="text-sm text-muted">
			New here? Read <ULink to="/about" class="text-primary">how the assessment works</ULink>.
			MediLinda was built with
			<ULink to="https://www.intellisoftkenya.com" target="_blank" class="text-primary">
				IntelliSOFT Consulting Ltd
			</ULink>
			and the
			<ULink to="https://web.pharmacyboardkenya.org/" target="_blank" class="text-primary">
				Pharmacy and Poisons Board
			</ULink>.
		</p>
	</div>
</template>

<script setup lang="ts">
import { fetchAdrsWithCausalityAndReviewCount } from "@/api/adr";
import { fetchCurrentUser } from "@/api/user";
import { useQuery } from "@tanstack/vue-query";
import { greeting, homeCards } from "~/utils/home";

// Only the total of each list matters, so each query asks for one row.
const count = (review?: string[]) =>
	useQuery({
		queryKey: ["adrs", "home", review ?? "all"],
		queryFn: async () =>
			(await fetchAdrsWithCausalityAndReviewCount({ page: 1, size: 1, review_status: review })).total,
	});

const all = count();
const needsReview = count(["needs_review"]);
const notApproved = count(["not_approved"]);

const { data: user } = useQuery({ queryKey: ["currentUser"], queryFn: fetchCurrentUser });

const cards = computed(() =>
	homeCards({
		all: all.data.value,
		needsReview: needsReview.data.value,
		notApproved: notApproved.data.value,
	}),
);

const isError = computed(() => all.isError.value || needsReview.isError.value || notApproved.isError.value);

function refetchAll() {
	all.refetch();
	needsReview.refetch();
	notApproved.refetch();
}

// The hour comes from the browser, after the page loads. The server's hour can differ,
// and the two would not match.
const hour = ref<number>();
onMounted(() => (hour.value = new Date().getHours()));

const title = computed(() => (hour.value === undefined ? "Welcome" : greeting(user.value, hour.value)));

useHead({ title: "Home | MediLinda" });
</script>
