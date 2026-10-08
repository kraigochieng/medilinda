import { auth } from "../../utils/auth";
import { handleVerifyApiKey } from "../../utils/verify-api-key";

export default defineEventHandler(async (event) => {
	const { key } = (await readBody<{ key?: string }>(event)) ?? {};

	const result = await handleVerifyApiKey({
		expectedSecret: process.env.INTERNAL_API_SECRET,
		providedSecret: getHeader(event, "x-internal-secret"),
		key,
		verify: (apiKey) => auth.api.verifyApiKey({ body: { key: apiKey } }),
	});

	if (result.status !== 200) {
		throw createError({ statusCode: result.status, statusMessage: result.message });
	}
	return result.body;
});
