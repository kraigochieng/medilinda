// The tabs of the ADR page. The active tab is in the page address (?tab=review), so a
// link from the list can open a tab, and a refresh keeps it.
export const ADR_TABS = [
	{ value: "details", label: "Details", icon: "i-lucide-file-text" },
	{ value: "prediction", label: "Prediction", icon: "i-lucide-brain-circuit" },
	{ value: "review", label: "Review", icon: "i-lucide-clipboard-check" },
	{ value: "history", label: "History", icon: "i-lucide-history" },
] as const;

export type AdrTab = (typeof ADR_TABS)[number]["value"];

export const DEFAULT_TAB: AdrTab = "details";

export function parseTab(value: unknown): AdrTab {
	const first = Array.isArray(value) ? value[0] : value;
	return ADR_TABS.find((tab) => tab.value === first)?.value ?? DEFAULT_TAB;
}

// The address query for a tab. The default tab has no parameter. Other parameters stay.
export function tabQuery(tab: AdrTab, current: Record<string, unknown>): Record<string, unknown> {
	const { tab: _old, ...rest } = current;
	return tab === DEFAULT_TAB ? rest : { ...rest, tab };
}

// A link to one tab of an ADR, for the list.
export function tabAddress(adrId: string, tab: AdrTab): string {
	return tab === DEFAULT_TAB ? `/adr/${adrId}` : `/adr/${adrId}?tab=${tab}`;
}

// The form sends the user here with ?created=1 or ?saved=1. Remove these after use.
export function withoutSaved(current: Record<string, unknown>): Record<string, unknown> {
	const { created: _created, saved: _saved, ...rest } = current;
	return rest;
}
