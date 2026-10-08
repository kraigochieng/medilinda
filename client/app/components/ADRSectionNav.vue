<template>
	<nav
		aria-label="Form sections"
		class="sticky top-0 z-10 rounded-lg border border-default bg-default p-3 text-sm lg:static lg:space-y-3"
	>
		<!-- A narrow screen: one slim bar. The list opens when it is needed. -->
		<button
			type="button"
			class="flex w-full items-center gap-3 lg:hidden"
			:aria-expanded="open"
			aria-controls="form-sections-list"
			@click="open = !open"
		>
			<span class="grow text-start font-medium" aria-live="polite">{{ progressText(progress) }}</span>
			<UProgress
				:model-value="progress.done"
				:max="Math.max(progress.total, 1)"
				size="sm"
				:color="progress.done === progress.total ? 'success' : 'primary'"
				class="w-20"
				aria-label="Required fields completed"
			/>
			<UIcon :name="open ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'" class="size-4 shrink-0" />
		</button>

		<!-- A wide screen: the same facts, always in view. -->
		<div class="hidden lg:block">
			<div class="mb-1 flex items-center justify-between">
				<span class="font-medium">Required fields</span>
				<span class="text-muted" aria-live="polite">{{ progress.done }} of {{ progress.total }}</span>
			</div>
			<UProgress
				:model-value="progress.done"
				:max="Math.max(progress.total, 1)"
				size="sm"
				:color="progress.done === progress.total ? 'success' : 'primary'"
				aria-label="Required fields completed"
			/>
		</div>

		<ol v-show="showList" id="form-sections-list" class="mt-3 space-y-0.5 lg:mt-0">
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
import { SECTIONS, progressText, type SectionState, type SectionStatus } from "~/utils/adr-sections";

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

// On a narrow screen the list is closed until the user opens it. On a wide screen it
// is always shown.
const isWide = useMediaQuery("(min-width: 1024px)");
const open = ref(false);
const showList = computed(() => isWide.value || open.value);

function go(id: string) {
	document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
	active.value = id;
	open.value = false;
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
