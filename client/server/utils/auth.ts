import { LibsqlDialect } from "@libsql/kysely-libsql";
import { createAuth } from "./auth-factory";

export const auth = createAuth({
	baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
	secret: process.env.BETTER_AUTH_SECRET,
	database: {
		dialect: new LibsqlDialect({
			url: process.env.TURSO_DATABASE_URL || "file:auth.db",
			authToken: process.env.TURSO_AUTH_TOKEN,
		}),
		type: "sqlite",
	},
});
