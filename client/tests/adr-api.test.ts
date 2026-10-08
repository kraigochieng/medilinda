import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
	deleteAdrById,
	fetchAdrsWithCausalityAndReviewCount,
	restoreAdrById,
} from "../app/api/adr";

const serverFetch = vi.fn();

beforeEach(() => {
	serverFetch.mockReset().mockResolvedValue({});
	vi.stubGlobal("useNuxtApp", () => ({ $serverFetch: serverFetch }));
});

afterEach(() => vi.unstubAllGlobals());

describe("ADR API calls", () => {
	it("deletes with DELETE /adrs/{id}", async () => {
		await deleteAdrById("abc");

		expect(serverFetch).toHaveBeenCalledWith("/adrs/abc", { method: "DELETE" });
	});

	it("restores with POST /adrs/{id}/restore", async () => {
		await restoreAdrById("abc");

		expect(serverFetch).toHaveBeenCalledWith("/adrs/abc/restore", { method: "POST" });
	});

	it("passes the search and filters to the list endpoint", async () => {
		const params = {
			page: 2,
			size: 20,
			query: "alice",
			causality_level: "likely",
			review_status: "needs_review",
		};

		await fetchAdrsWithCausalityAndReviewCount(params);

		expect(serverFetch).toHaveBeenCalledWith(
			"/adrs-details/with-causality-and-review-count",
			{ method: "GET", query: params },
		);
	});

	it("surfaces a failed list request as an error", async () => {
		serverFetch.mockRejectedValue(new Error("boom"));

		await expect(fetchAdrsWithCausalityAndReviewCount({ page: 1 })).rejects.toThrow("boom");
	});
});
