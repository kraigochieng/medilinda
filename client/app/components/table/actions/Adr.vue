<template>
	<DropdownMenu>
		<DropdownMenuTrigger as-child>
			<Button variant="ghost" class="w-8 h-8 p-0">
				<span class="sr-only">Open menu</span>
				<MoreHorizontal class="w-4 h-4" />
			</Button>
		</DropdownMenuTrigger>
		<DropdownMenuContent align="end">
			<DropdownMenuLabel>Actions</DropdownMenuLabel>
			<DropdownMenuItem @mouseup="handleView">View ADR</DropdownMenuItem>
			<DropdownMenuItem @mouseup="handleEdit">Edit ADR</DropdownMenuItem>
			<DropdownMenuItem @mouseup="handleDelete"
				>Delete ADR</DropdownMenuItem
			>
			<!-- <DropdownMenuItem>
				<AlertDialog>
					<AlertDialogTrigger as-child>
						<p class="dropdowm-menu-item-class">Delete ADR</p>
					</AlertDialogTrigger>
					<AlertDialogContent>
						<AlertDialogHeader>
							<AlertDialogTitle>Are you sure?</AlertDialogTitle>
							<AlertDialogDescription>
								This action cannot be undone. This will
								permanently delete this record
							</AlertDialogDescription>
						</AlertDialogHeader>
						<AlertDialogFooter>
							<AlertDialogCancel>Cancel</AlertDialogCancel>
							<AlertDialogAction @mouseup="handleDelete">
								Continue
							</AlertDialogAction>
						</AlertDialogFooter>
					</AlertDialogContent>
				</AlertDialog>
			</DropdownMenuItem> -->
		</DropdownMenuContent>
	</DropdownMenu>
</template>

<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal } from "lucide-vue-next";

const props = defineProps<{
	row: {
		adr_id: string;
	};
}>();

const router = useRouter();

function handleView() {
	router.push(`/adr/${props.row.adr_id}`);
}

function handleEdit() {
	router.push(`/adr/${props.row.adr_id}/edit`);
}
const isOpen = ref(false);

const authStore = useAuthStore();

async function handleDelete() {
	if (!confirm("Are you sure you want to delete this review?")) {
		// User canceled
		return;
	}

	const runtimeConfig = useRuntimeConfig();
	const serverApi = runtimeConfig.public.serverApi;

	try {
		await $fetch(`${serverApi}/adr/${props.row.adr_id}`, {
			method: "DELETE",
			headers: {
				Authorization: `Bearer ${authStore.accessToken}`,
			},
		});
		// Optionally show success message here
		window.location.reload();
	} catch (error) {
		// Handle error, e.g. show error notification
		alert("Failed to delete the review. Please try again.");
	}
}
</script>

<style scoped>
.dropdowm-menu-item-class {
	@apply relative flex cursor-default select-none items-center rounded-sm gap-2 px-2 py-1.5 text-sm outline-none transition-colors focus:bg-neutral-100 focus:text-neutral-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&>svg]:size-4 [&>svg]:shrink-0 dark:focus:bg-neutral-800 dark:focus:text-neutral-50;
}
</style>
