import { timingSafeEqual } from "node:crypto";
import { auth } from "../../utils/auth";

// Server-to-server only: FastAPI calls this to check an `x-api-key`.
// Better Auth does not expose api-key verification over HTTP.
function secretsMatch(a: string, b: string) {
	const left = Buffer.from(a);
	const right = Buffer.from(b);
	return left.length === right.length && timingSafeEqual(left, right);
}

export default defineEventHandler(async (event) => {
	const secret = process.env.INTERNAL_API_SECRET;
	const provided = getHeader(event, "x-internal-secret") ?? "";

	if (!secret || !secretsMatch(provided, secret)) {
		throw createError({ statusCode: 401, statusMessage: "Unauthorized" });
	}

	const { key } = await readBody<{ key?: string }>(event);
	if (!key) {
		throw createError({ statusCode: 400, statusMessage: "Missing key" });
	}

	return await auth.api.verifyApiKey({ body: { key } });
});
