import { defineStore } from "pinia";
import { getCurrentUser, postToken } from "@/api/auth";

import type {
	LoginCredentials,
	SignUpDetails,
	TokenResponse,
} from "@/types/auth";
import type { UserDetails } from "@/types/user";
import humps from "humps";

function getServerApi() {
	const runtimeConfig = useRuntimeConfig();
	return runtimeConfig.public.serverApi;
}

export const useAuthStore = defineStore("auth", () => {
	const accessToken = useCookie("accessToken"); // Persist in cookies
	// const accessToken = useCookie<string | null>("accessToken", {
	// 	default: () => null,
	// 	sameSite: "strict",
	// 	secure: import.meta.server ? false : true, // Only secure in production
	// });
	const refreshToken = useCookie("refreshToken"); // Persist in cookies
	const user = ref<UserDetails | null>(null);
	// const isAuthenticated = computed(() => !!accessToken.value);
	const isAuthenticated = ref(false);
	// Error Booleans
	const isSignupError = ref(false);
	const isLoginError = ref(false);

	watchEffect(() => {
		// console.log("Before update - isAuthenticated:", isAuthenticated.value);
		isAuthenticated.value = !!accessToken.value;
		// console.log(
		// 	"After update - isAuthenticated:",
		// 	isAuthenticated.value,
		// 	"Access Token:",
		// 	accessToken.value
		// );
	});

	async function signup(details: SignUpDetails) {
		isSignupError.value = false;
		// isAuthenticated.value = false;

		const { status, error } = await postSignup(details);

		if (status.value == "success") {
			console.log("Login successful, setting tokens...");
			// const response = await getCurrentUser();

			// user.value = humps.camelizeKeys(response?.data.value) ?? null;
			// const {
			// 	data: userData,
			// 	status: userStatus,
			// 	error: userError,
			// } = await getCurrentUser();
			// if (userStatus.value == "success") {
			// 	user.value = userData.value;
			// }
			// isAuthenticated.value = true;
			navigateTo("/adr");
		}

		if (error.value?.statusCode == 400) {
			isSignupError.value = true;
		}
	}

	async function login(credentials: LoginCredentials) {
		isLoginError.value = false;
		// isAuthenticated.value = false;
		// const { status, data, error } = await postToken(credentials);
		const body = new URLSearchParams();

		body.set("username", credentials.username);
		body.set("password", credentials.password);

		// const { status, data, error } = await useFetch<TokenResponse>(
		// 	`${getServerApi()}/token`,
		// 	{
		// 		method: "POST",
		// 		headers: {
		// 			"Content-Type": "application/x-www-form-urlencoded",
		// 		},
		// 		body: body,
		// 	}
		// );

		const { status, data, error } = await postToken(credentials);
		if (status.value == "success" && data.value) {
			// await nextTick();
			accessToken.value = data.value.access_token;
			refreshToken.value = data.value.refresh_token;
			// isAuthenticated.value = true;
			// console.log("data.value", data.value);
			// console.log("data.value.accessToken", data.value.access_token);
			navigateTo("/adr");

			// const {
			// 	data: userData,
			// 	status: userStatus,
			// 	error: userError,
			// } = await getCurrentUser();
			// if (userStatus.value == "success") {
			// 	user.value = userData.value;
			// 	console.log("user in store", user.value);
			// }
		}

		if (status.value == "error") {
			accessToken.value = "";
			refreshToken.value = "";
			isLoginError.value = true;
		}
	}

	function logout() {
		accessToken.value = "";
		refreshToken.value = "";
		user.value = null;
		isSignupError.value = false;
		isLoginError.value = false;
		// isAuthenticated.value = false;
		navigateTo("/auth/login");
	}

	return {
		accessToken,
		refreshToken,
		user,
		signup,
		login,
		logout,
		isLoginError,
		isSignupError,
		isAuthenticated,
	};
});
