<template>
	<nav aria-label="Form sections" class="space-y-3 rounded-lg border border-default p-3 text-sm">
		<div>
			<div class="mb-1 flex items-center justify-between">
				<span class="font-medium">Required fields</span>
				<span class="text-muted" aria-live="polite">{{ progress.done }} of {{ progress.total }}</span>
			</div>
			<UProgress
				:model-value="progress.done"
				:max="progress.total"
				size="sm"
				:color="progress.done === progress.total ? 'success' : 'primary'"
				aria-label="Required fields completed"
			/>
		</div>

		<ol class="space-y-0.5">
			<li v-for="item in statuses" :key="item.section.id">
				<a
					:href="`#${item.section.id}`"
					:aria-current="active === item.section.id ? 'location' : undefined"
					class="flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-elevated"
					:class="active === item.section.id ? 'bg-elevated font-medium' : ''"
					@click.prevent="go(item.section.id)"
				>
					<UIcon :name="ICON[item.state]" :class="['size-4 shrink-0', COLOR[item.state]]" />
					<span class="grow">{{ item.section.label }}</span>
					<span class="sr-only">{{ LABEL[item.state] }}</span>
					<span v-if="item.state === 'error'" class="text-xs font-medium text-error" aria-hidden="true">
						{{ item.problems }}
					</span>
				</a>
			</li>
			<li>
				<a
					href="#submit"
					class="flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-elevated"
					@click.prevent="go('submit')"
				>
					<UIcon name="i-lucide-save" class="size-4 shrink-0 text-muted" />
					<span>Save</span>
				</a>
			</li>
		</ol>
	</nav>
</template>

<script setup lang="ts">
import { SECTIONS, type SectionState, type SectionStatus } from "~/utils/adr-sections";

const SECTION_IDS = SECTIONS.map((section) => section.id);

defineProps<{
	statuses: SectionStatus[];
	progress: { done: number; total: number };
}>();

const ICON: Record<SectionState, string> = {
	complete: "i-lucide-circle-check",
	incomplete: "i-lucide-circle",
	error: "i-lucide-circle-alert",
	optional: "i-lucide-circle-dashed",
};
const COLOR: Record<SectionState, string> = {
	complete: "text-success",
	incomplete: "text-warning",
	error: "text-error",
	optional: "text-muted",
};
const LABEL: Record<SectionState, string> = {
	complete: "complete",
	incomplete: "needs attention",
	error: "has errors",
	optional: "optional",
};

const active = ref<string>("");

function go(id: string) {
	document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
	active.value = id;
}

// Highlight the section being read: the last heading to reach the top of the view.
let observer: IntersectionObserver | undefined;

onMounted(() => {
	observer = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) {
				if (entry.isIntersecting) active.value = entry.target.id;
			}
		},
		{ rootMargin: "-10% 0px -75% 0px" }
	);

	for (const id of [...SECTION_IDS, "submit"]) {
		const element = document.getElementById(id);
		if (element) observer.observe(element);
	}
});

onBeforeUnmount(() => observer?.disconnect());
</script>
