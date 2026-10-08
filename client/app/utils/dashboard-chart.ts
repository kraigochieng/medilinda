// Small rules for the dashboard charts, kept apart from the components so they can be tested.
import type { MetricValue } from "~/types/dashboard";

export const MAX_LABEL = 22;

// A long label (an institution name) would push the chart aside. Cut it and mark the cut.
export function shorten(label: string): string {
	return label.length <= MAX_LABEL ? label : `${label.slice(0, MAX_LABEL - 1).trimEnd()}…`;
}

// The chart asks for a label at each tick of its axis. A tick that is not a whole
// number, or has no bar, gets no label.
export function labelAt(data: MetricValue[] | undefined, index: number): string {
	return Number.isInteger(index) ? (data?.[index]?.metric ?? "") : "";
}

// A chart of only zeros says nothing, so the card shows an empty message instead.
export function hasData(data: MetricValue[] | undefined): boolean {
	return !!data?.some((point) => point.value > 0);
}
