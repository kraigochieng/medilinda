import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fetchAdrActivity, fetchDeletedAdrs } from "../app/api/audit";

const serverFetch = vi.fn();

beforeEach(() => {
	serverFetch.mockReset().mockResolvedValue({ items: [], total: 0, page: 1, size: 20, pages: 0 });
	vi.stubGlobal("useNuxtApp", () => ({ $serverFetch: serverFetch }));
});

afterEach(() => vi.unstubAllGlobals());

describe("audit API calls", () => {
	it("reads an ADR's activity with GET /adrs/{id}/activity", async () => {
		await fetchAdrActivity("abc", { page: 2, size: 20 });

		expect(serverFetch).toHaveBeenCalledWith("/adrs/abc/activity", {
			method: "GET",
			query: { page: 2, size: 20 },
		});
	});

	it("lists deleted ADRs with GET /audit-logs/deleted-adrs", async () => {
		await fetchDeletedAdrs({ page: 1 });

		expect(serverFetch).toHaveBeenCalledWith("/audit-logs/deleted-adrs", {
			method: "GET",
			query: { page: 1 },
		});
	});

	it("passes errors on so the page can show them", async () => {
		serverFetch.mockRejectedValue(new Error("offline"));

		await expect(fetchAdrActivity("abc")).rejects.toThrow("offline");
		await expect(fetchDeletedAdrs()).rejects.toThrow("offline");
	});
});
