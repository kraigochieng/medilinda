<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/toast";
import ToastAction from "@/components/ui/toast/ToastAction.vue";
import type { SMSMessageGetResponse } from "@/types/sms_message";
import { MoreHorizontal } from "lucide-vue-next";

const { toast } = useToast();

const props = defineProps<{
	row: {
		adr_id: string;
		sms_count: number;
		patient_name: string;
		medical_institution_name: string;
	};
}>();

const router = useRouter();

const authStore = useAuthStore();

function handleViewADR() {
	router.push(`/adr/${props.row.adr_id}`);
}

async function handleSend() {
	const response = await $fetch<SMSMessageGetResponse[]>(
		`${useRuntimeConfig().public.serverApi}/send_additional_info_request`,
		{
			method: "POST",
			headers: {
				Authorization: `Bearer ${authStore.accessToken}`,
			},
			body: {
				adr_id: props.row.adr_id,
			},
		}
	);
	response.map((message) => {
		if (message.status_code == 100) {
			console.log("Toast message:", message);
			toast({
				title: message.status,
				description: h("div", [
					h(
						"p",
						`Medical Institution Name: ${props.row.medical_institution_name}`
					),
					h("p", `Medical Institution Number: ${message.number}`),
					h("p", `Patient Name: ${props.row.patient_name}`),
				]),
			});
		} else {
			toast({
				title: message.status,
				description: message.content,
				variant: "destructive",
				action: h(
					ToastAction,
					{ altText: "Error" },
					{ default: () => "Try again" }
				),
			});
		}
	});

	setTimeout(() => {
		window.location.reload();
	}, 2500);
}
</script>

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
			<DropdownMenuItem @mouseup="handleViewADR">
				View ADR
			</DropdownMenuItem>
			<DropdownMenuItem @mouseup="handleSend">
				{{
					props.row.sms_count > 0
						? "Resend Additional Information Request"
						: "Send Additional Information Request"
				}}
			</DropdownMenuItem>
			<DropdownMenuItem v-if="props.row.sms_count > 0">
				Make Unclassifiable
			</DropdownMenuItem>
		</DropdownMenuContent>
	</DropdownMenu>
</template>
