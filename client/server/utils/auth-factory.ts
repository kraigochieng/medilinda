import { apiKey } from "@better-auth/api-key";
import { betterAuth } from "better-auth";
import { jwt, username } from "better-auth/plugins";
import { hashUserPassword, verifyUserPassword } from "./password";

export const JWT_AUDIENCE = "medilinda-api";

type CreateAuthOptions = {
	baseURL: string;
	secret: string | undefined;
	// A better-auth database config (e.g. a Kysely dialect).
	database: Parameters<typeof betterAuth>[0]["database"];
};

export function createAuth({ baseURL, secret, database }: CreateAuthOptions) {
	return betterAuth({
		baseURL,
		secret,
		database,
		trustedOrigins: [baseURL],
		emailAndPassword: {
			enabled: true,
			password: {
				hash: hashUserPassword,
				verify: verifyUserPassword,
			},
		},
		user: {
			additionalFields: {
				firstName: { type: "string", required: false, input: true },
				lastName: { type: "string", required: false, input: true },
				disabled: { type: "boolean", required: false, defaultValue: false, input: false },
			},
		},
		plugins: [
			// Legacy users have one-letter usernames (A-Z). The signup form still
			// asks new users for at least 3 characters.
			username({ minUsernameLength: 1 }),
			jwt({
				jwt: {
					issuer: baseURL,
					audience: JWT_AUDIENCE,
					expirationTime: "15m",
					// FastAPI reads these claims; `sub` is the user id (default).
					definePayload: ({ user }) => ({
						username: user.username,
						first_name: user.firstName,
						last_name: user.lastName,
						disabled: user.disabled ?? false,
					}),
				},
			}),
			apiKey(),
		],
	});
}
