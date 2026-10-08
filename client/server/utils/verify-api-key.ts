import { timingSafeEqual } from "node:crypto";

const secretsMatch = (a: string, b: string) => {
	const left = Buffer.from(a);
	const right = Buffer.from(b);
	return left.length === right.length && timingSafeEqual(left, right);
};

type VerifyInput = {
	expectedSecret: string | undefined;
	providedSecret: string | undefined;
	key: string | undefined;
	verify: (key: string) => Promise<unknown>;
};

// Server-to-server only: FastAPI calls this to check an `x-api-key`.
// Better Auth does not expose api-key verification over http.
export async function handleVerifyApiKey({
	expectedSecret,
	providedSecret,
	key,
	verify,
}: VerifyInput): Promise<{ status: number; body?: unknown; message?: string }> {
	if (!expectedSecret || !secretsMatch(providedSecret ?? "", expectedSecret)) {
		return { status: 401, message: "Unauthorized" };
	}
	if (!key) {
		return { status: 400, message: "Missing key" };
	}
	return { status: 200, body: await verify(key) };
}
