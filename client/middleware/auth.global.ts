import { useAuthStore } from "~/stores/auth";

export default defineNuxtRouteMiddleware(async (to, from) => {
	//	Allow access to login and signup pages
	if (to.path === "/auth/login" || to.path === "/auth/signup") return;

	const authStore = useAuthStore();

	// // Debugging logs
	// console.log(
	// 	"Middleware Check - isAuthenticated:",
	// 	authStore.isAuthenticated
	// );
	// console.log("Middleware Check - Access Token:", authStore.accessToken);

	// Wait for authentication state to update before redirecting
	await nextTick();
	// Redirect to login if not authenticated
	if (!authStore.isAuthenticated) {
		return navigateTo("/auth/login");
	}
		// // Read access token from cookies directly
		// const accessToken = useCookie("accessToken");

		// // Debugging logs
		// console.log("Middleware Check - Access Token:", accessToken.value);

		// if (!accessToken.value) {
		// 	console.log("Redirecting to login...");
		// 	return navigateTo("/auth/login");
		// }
	
});

// export default defineNuxtRouteMiddleware((to, from) => {
// 	const accessToken = useCookie("accessToken");

// 	if (!accessToken.value) {
// 		return navigateTo("/auth/login"); // Redirect to login if no token
// 	}
// });
