// export const useAuth = () => {
// 	const config = useRuntimeConfig();

// 	const refreshToken = async () => {
// 		try {
// 			const refreshToken = localStorage.getItem("refresh_token");

// 			if (!refreshToken) {
// 				localStorage.clear();
// 				return null;
// 			}

// 			const response = await fetch(
// 				`${config.public.serverApi}/token/refresh`,
// 				{
// 					method: "POST",
// 					headers: { "Content-Type": "application/json" },
// 					body: JSON.stringify({ refresh_token: refreshToken }),
// 				}
// 			);

// 			if (!response.ok) {
// 				localStorage.clear();
// 				return null;
// 			}

// 			const data = await response.json();
// 			localStorage.setItem("access_token", data.access_token);
// 			return data.access_token;
// 		} catch (error) {
// 			return null;
// 		}
// 	};

// 	const getAuthHeaders = async () => {
// 		let accessToken = localStorage.getItem("access_token");

// 		if (!accessToken) {
// 			accessToken = await refreshToken();
// 		}

// 		return accessToken ? { Authorization: `Bearer ${accessToken}` } : null;
// 	};

// 	return { refreshToken, getAuthHeaders };
// };
