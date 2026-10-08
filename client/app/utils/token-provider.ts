// Reads the `exp` claim (in ms) from a JWT without verifying it.
export function readTokenExpiry(token: string): number {
	try {
		const payload = JSON.parse(atob(token.split(".")[1] ?? ""));
		return payload.exp * 1000;
	} catch {
		return 0;
	}
}

type TokenProviderOptions = {
	fetchToken: () => Promise<string>;
	// Only cache in the browser. A server-side cache would leak between users.
	cache: boolean;
	now?: () => number;
	skewMs?: number;
};

export function createTokenProvider({
	fetchToken,
	cache,
	now = Date.now,
	skewMs = 30_000,
}: TokenProviderOptions) {
	let cached: { value: string; expiresAt: number } | null = null;

	return {
		async get(): Promise<string | null> {
			if (cache && cached && cached.expiresAt - skewMs > now()) {
				return cached.value;
			}
			try {
				const token = await fetchToken();
				if (cache) {
					cached = { value: token, expiresAt: readTokenExpiry(token) };
				}
				return token;
			} catch {
				cached = null;
				return null;
			}
		},
		clear() {
			cached = null;
		},
	};
}
