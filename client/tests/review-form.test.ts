import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { deleteReview, postReview, putReview } from "../app/api/review";
import {
	apiErrorMessage,
	proposableLevels,
	reviewFormSchema,
	toReviewPayload,
	toReviewUpdate,
} from "../app/utils/review-form";

const check = (form: object, predicted = "likely") => reviewFormSchema(predicted).safeParse(form);
const messages = (result: ReturnType<typeof check>) => result.error?.issues.map((i) => i.message) ?? [];
const paths = (result: ReturnType<typeof check>) => result.error?.issues.map((i) => i.path.join(".")) ?? [];

describe("the review form's rules", () => {
	it("accepts an approval with nothing else", () => {
		expect(check({ approved: true }).success).toBe(true);
	});

	it("needs a choice between approve and not", () => {
		const result = check({});

		expect(result.success).toBe(false);
		expect(messages(result)).toEqual(["Choose whether you approve the prediction."]);
	});

	it("accepts a rejection with a different level and a reason", () => {
		expect(
			check({ approved: false, proposed_causality_level: "possible", reason: "Unclear dechallenge" }).success,
		).toBe(true);
	});

	it("asks a rejection for a proposed level and a reason, naming each field", () => {
		const result = check({ approved: false });

		expect(paths(result)).toEqual(["proposed_causality_level", "reason"]);
		expect(messages(result)[0]).toMatch(/Choose the causality level/);
		expect(messages(result)[1]).toMatch(/reason/);
	});

	it("does not accept the predicted level as the proposal", () => {
		const result = check({ approved: false, proposed_causality_level: "likely", reason: "Because" });

		expect(paths(result)).toEqual(["proposed_causality_level"]);
		expect(messages(result)[0]).toMatch(/differ/);
	});

	it("treats a reason of only spaces, or one that is too short, as missing", () => {
		for (const reason of ["", "   ", "ab", " a "]) {
			const result = check({ approved: false, proposed_causality_level: "possible", reason });
			expect(paths(result), JSON.stringify(reason)).toEqual(["reason"]);
		}
	});

	it("does not ask an approval for a reason or a proposed level", () => {
		expect(check({ approved: true, reason: "", proposed_causality_level: undefined }).success).toBe(true);
	});
});

describe("proposable levels", () => {
	it("are all the levels except the predicted one", () => {
		const values = proposableLevels("likely").map((o) => o.value);

		expect(values).not.toContain("likely");
		expect(values).toEqual(["certain", "possible", "unlikely", "unclassified", "unclassifiable"]);
	});

	it("are all the levels when nothing is predicted", () => {
		expect(proposableLevels(undefined)).toHaveLength(6);
	});
});

describe("what is sent to the server", () => {
	it("drops the proposed level from an approval and trims the reason", () => {
		expect(
			toReviewUpdate({ approved: true, proposed_causality_level: "certain", reason: "  Agree  " }),
		).toEqual({ approved: true, proposed_causality_level: undefined, reason: "Agree" });
	});

	it("keeps the proposed level of a rejection", () => {
		expect(
			toReviewUpdate({ approved: false, proposed_causality_level: "possible", reason: "Unclear" }),
		).toEqual({ approved: false, proposed_causality_level: "possible", reason: "Unclear" });
	});

	it("leaves out a blank reason and never sends a user id", () => {
		const payload = toReviewPayload({ approved: true, reason: "   " }, "cal-1");

		expect(payload).toEqual({
			causality_assessment_level_id: "cal-1",
			approved: true,
			proposed_causality_level: undefined,
			reason: undefined,
		});
		expect(payload).not.toHaveProperty("user_id");
	});
});

describe("apiErrorMessage", () => {
	it("shows the message the server sent", () => {
		expect(apiErrorMessage({ data: { error: "You have already reviewed this assessment." } })).toBe(
			"You have already reviewed this assessment.",
		);
	});

	it("falls back to detail, then to something readable for a status code", () => {
		expect(apiErrorMessage({ data: { detail: "Could not validate credentials" } })).toBe(
			"Could not validate credentials",
		);
		expect(apiErrorMessage({ statusCode: 404 })).toMatch(/could not be found/);
		expect(apiErrorMessage({ statusCode: 403 })).toMatch(/not allowed/);
	});

	it("never shows a raw error object", () => {
		expect(apiErrorMessage(new Error("[POST] http://x: 500"))).toBe("Something went wrong. Try again.");
		expect(apiErrorMessage(null, "custom")).toBe("custom");
		expect(apiErrorMessage({ data: { error: { nested: true } } })).toBe("Something went wrong. Try again.");
	});
});

describe("review API calls", () => {
	const serverFetch = vi.fn();

	beforeEach(() => {
		serverFetch.mockReset().mockResolvedValue({});
		vi.stubGlobal("useNuxtApp", () => ({ $serverFetch: serverFetch }));
	});
	afterEach(() => vi.unstubAllGlobals());

	it("adds a review with POST /reviews/", async () => {
		const body = { causality_assessment_level_id: "c1", approved: true };
		await postReview(body);

		expect(serverFetch).toHaveBeenCalledWith("/reviews/", { method: "POST", body });
	});

	it("changes a review with PUT /reviews/{id}", async () => {
		const body = { approved: false, proposed_causality_level: "possible", reason: "Unclear" };
		await putReview("r1", body);

		expect(serverFetch).toHaveBeenCalledWith("/reviews/r1", { method: "PUT", body });
	});

	it("deletes a review with DELETE /reviews/{id}", async () => {
		await deleteReview("r1");

		expect(serverFetch).toHaveBeenCalledWith("/reviews/r1", { method: "DELETE" });
	});

	it("passes a server error on", async () => {
		serverFetch.mockRejectedValue({ data: { error: "nope" } });

		await expect(postReview({ causality_assessment_level_id: "c", approved: true })).rejects.toEqual({
			data: { error: "nope" },
		});
	});
});
