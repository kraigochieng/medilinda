import { apiKey } from "@better-auth/api-key";
import { LibsqlDialect } from "@libsql/kysely-libsql";
import { betterAuth } from "better-auth";
import { hashPassword, verifyPassword } from "better-auth/crypto";
import { jwt, username } from "better-auth/plugins";
import bcrypt from "bcryptjs";

const baseURL = process.env.BETTER_AUTH_URL || "http://localhost:3000";

export const JWT_AUDIENCE = "medilinda-api";

// Users migrated from the old FastAPI auth keep their bcrypt hashes.
// Everyone else uses better-auth's default scrypt.
const isBcryptHash = (hash: string) => /^\$2[abxy]\$/.test(hash);

export const auth = betterAuth({
	baseURL,
	secret: process.env.BETTER_AUTH_SECRET,
	database: {
		dialect: new LibsqlDialect({
			url: process.env.TURSO_DATABASE_URL || "file:auth.db",
			authToken: process.env.TURSO_AUTH_TOKEN,
		}),
		type: "sqlite",
	},
	trustedOrigins: [baseURL],
	emailAndPassword: {
		enabled: true,
		password: {
			hash: (password) => hashPassword(password),
			verify: ({ hash, password }) =>
				isBcryptHash(hash)
					? bcrypt.compare(password, hash)
					: verifyPassword({ hash, password }),
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
		username(),
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
