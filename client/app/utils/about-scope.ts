// The section "What MediLinda does, and what it does not do" on the About page. It is
// data, so a test can check each claim and the words stay the same on every page.

import { MODEL_FACTS, formatCount } from "~/utils/model-facts";

export const SCOPE_ID = "scope";
export const SCOPE_HEADING = "What MediLinda does, and what it does not do";

export const SCOPE_PURPOSE =
	"MediLinda is a fourth-year project. It shows how causality assessment in pharmacovigilance can work with a model, its reasons, and a review by experts.";

export const SCOPE_DOES: string[] = [
	"It captures the ADR report in one structured form.",
	"It predicts a causality assessment level in seconds. It shows the reasons for the level (SHAP).",
	"It lets pharmacovigilance experts review the prediction. They approve it, or they propose another level with a reason.",
	"It sends the result to the reporting facility. An approved, certain prediction becomes an alert. A report the model cannot classify becomes a request for more information.",
	"It keeps the history of every change. It shows a dashboard.",
];

export const SCOPE_DOES_NOT: string[] = [
	"It does not manage what happens after an alert reaches a facility. That covers the investigation at the facility, the care of the patient, and any change of treatment.",
	"It does not track if a facility read, answered or acted on a message. It does not close a case.",
	"It does not take regulatory action. It does not report to national or international systems.",
	"It does not make clinical decisions. The prediction is a first opinion. The expert decides.",
];

export const SCOPE_MODEL_HEADING = "What the model knows";

export const SCOPE_MODEL: string[] = [
	"The form and the model cover four first-line TB medicines: rifampicin, isoniazid, pyrazinamide and ethambutol.",
	"A report about another medicine cannot be entered or judged.",
	"The model predicts four levels: certain, likely, possible and unlikely. The server sets the levels unclassified and unclassifiable by rule, when facts are missing.",
	"The model covers TB patients in Kenya.",
];

export const SCOPE_DATA_HEADING = "The data, and its limits";

export const SCOPE_DATA: string[] = [
	`The data is synthetic. It holds ${formatCount(MODEL_FACTS.rows)} reports. A sampler built each case in causal order: the patient, the history, the medicines, the reaction, the dates, and the follow-up.`,
	"The sampler uses the totals of two quarterly reports of the Pharmacy and Poisons Board (Q2 and Q3 of 2025/26) and published facts on TB medicines. The reports hold all patients, not only TB patients. Where no source gave a number, the project chose one.",
	"The WHO-UMC level of each report is the output of rules that read the facts of the report. The rules did not choose the report to fit a level.",
	"The mix of levels comes from the rules. About 1 report in 100 is certain. About 5 labels in 100 move one step, because real assessors disagree.",
	"The scores show how well a model learns the rules. They do not show clinical accuracy.",
	"The model in the app reads only the fields that the app collects today. With these fields it predicts poorly. It finds few certain cases and often says certain by mistake.",
	"A model that also reads the history, the other medicines, and the lab results scores much higher on this data. The app does not collect these fields yet.",
	"MediLinda is a simulated solution. It shows what such a system can do. It is not for use on real patients.",
];
