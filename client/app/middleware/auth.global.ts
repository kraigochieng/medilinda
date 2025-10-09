export default defineNuxtRouteMiddleware(async (to, from) => {
	// const token = useCookie("medilindaBearerToken").value;

	// // If no token at all, redirect early
	// if (!token) {
	// 	return navigateTo("/auth/login");
	// }

	// try {
	// 	const { $serverFetch } = useNuxtApp();
	// 	await $serverFetch("/users/me"); // protected route
	// } catch (error: any) {
	// 	if (error?.response?.status === 401) {
	// 		return navigateTo("/auth/login");
	// 	}
	// }
});
