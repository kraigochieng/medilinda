import type { CausalityAssessmentLevelEnum } from "./adr";

export interface ClassRanking {
	label?: string;
	baseValue: number;
	shapValue: number;
	baseShapValue: number;
}
