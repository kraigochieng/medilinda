import { apiKeyClient } from "@better-auth/api-key/client";
import { jwtClient, usernameClient } from "better-auth/client/plugins";
import { createAuthClient } from "better-auth/vue";

export const authClient = createAuthClient({
	plugins: [usernameClient(), jwtClient(), apiKeyClient()],
});
