// What the API keys page says about a key. Kept apart from the page so it can be tested.
export interface KeyExpiry {
	expiresAt: Date | string | null | undefined;
}

const DAY = new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeZone: "UTC" });

export function describeKey(key: KeyExpiry, now = new Date()): { text: string; expired: boolean } {
	const at = key.expiresAt ? new Date(key.expiresAt) : null;
	if (!at || Number.isNaN(at.getTime())) return { text: "No expiry", expired: false };

	const expired = at.getTime() <= now.getTime();
	return { text: `${expired ? "Expired" : "Expires"} ${DAY.format(at)}`, expired };
}

// The form asks for days. The server wants seconds. Nothing valid means no expiry.
export function expiryInSeconds(days: number | null | undefined): number | undefined {
	if (typeof days !== "number" || !Number.isFinite(days)) return undefined;
	const whole = Math.floor(days);
	return whole >= 1 ? whole * 86_400 : undefined;
}
