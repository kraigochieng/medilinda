import { defineStore } from "pinia";
import { getCurrentUser, postToken } from "@/app/api/auth";

import type {
	LoginCredentials,
	SignUpDetails,
	TokenResponse,
} from "@/app/types/auth";
import type { UserDetails } from "@/app/types/user";

export const useAuthStore = defineStore("auth", () => {
	const accessToken = useCookie<string | null>("accessToken"); // Persist in cookies
	const user = ref<UserDetails | null>(null);
	const isAuthenticated = computed(() => !!accessToken.value);

	function setAccessToken(token: string) {
		accessToken.value = token;
	}

	function logout() {
		accessToken.value = null;
		user.value = null;
		navigateTo("/auth/login");
	}

	return {
		accessToken,
		user,
		logout,
		isAuthenticated,
		setAccessToken,
	};
});
