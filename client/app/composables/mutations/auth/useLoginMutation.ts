import { postToken } from "@/app/api/auth";
import { useAuthStore } from "@/stores/auth";
import { useMutation } from "@tanstack/vue-query";

export function useLoginMutation() {
	const authStore = useAuthStore();

	return useMutation({
		mutationFn: postToken,

		onSuccess: (data) => {
			authStore.setAccessToken(data.access_token);
			navigateTo("/adr");
		},
	});
}
