// The story the About page tells: one case, from a suspected reaction to a safer
// patient. It is data, so a test can check the order of the stages and that every
// page it names exists.
import { CAUSALITY_LEVELS } from "~/utils/causality-levels";

export interface StoryPlace {
	label: string;
	to: string;
	note: string;
}

export interface StoryDefinition {
	term: string;
	text: string;
}

export interface StoryStep {
	id: "suspect" | "report" | "predict" | "review" | "communicate" | "learn";
	stage: string;
	icon: string;
	title: string;
	story: string;
	definitions: StoryDefinition[];
	where: StoryPlace[];
	levels?: string[]; // the levels the model can predict, shown as badges
}

export const STORY: StoryStep[] = [
	{
		id: "suspect",
		stage: "Step 1",
		icon: "i-lucide-stethoscope",
		title: "A patient reacts to a medicine",
		story:
			"A nurse treats a patient for tuberculosis. The patient takes rifampicin, isoniazid, pyrazinamide and ethambutol. A few weeks later, the patient has a rash, or pain in the belly, or yellow eyes. The nurse asks one question. Did the medicine cause this?",
		definitions: [
			{
				term: "ADR",
				text: "An adverse drug reaction is a harmful, unwanted response to a medicine. It happens even when the medicine is used the right way.",
			},
			{
				term: "Pharmacovigilance",
				text: "This is the work of finding, judging and preventing the harm that medicines cause after they reach patients.",
			},
		],
		where: [],
	},
	{
		id: "report",
		stage: "Step 2",
		icon: "i-lucide-file-pen-line",
		title: "The case is written down",
		story:
			"The nurse reports the case. The form has six sections. They cover the health facility, the patient, the reaction, each medicine, what happened when the medicine stopped or restarted, and how serious the event was. The form saves a draft as you type. It marks the fields that are required.",
		definitions: [
			{
				term: "Dechallenge",
				text: "What happens to the reaction when the suspected medicine is stopped. If it gets better, the medicine is more likely the cause.",
			},
			{
				term: "Rechallenge",
				text: "What happens when the medicine is given again. If the reaction comes back, the medicine is very likely the cause.",
			},
		],
		where: [
			{
				label: "Add ADR",
				to: "/adr/add",
				note: "The report form, with a list of its sections and a count of the required fields.",
			},
		],
	},
	{
		id: "predict",
		stage: "Step 3",
		icon: "i-lucide-brain-circuit",
		title: "The model predicts how likely the medicine is the cause",
		story:
			"When the report is saved, a machine learning model reads it. It predicts one of six levels. The prediction is a first opinion. It is not the final answer. The model also shows its reasons, so a person can check them.",
		definitions: [
			{
				term: "Causality assessment",
				text: "A judgement of how likely it is that a medicine caused a reaction. Experts use set criteria to make it.",
			},
			{
				term: "SHAP",
				text: "A method that shows how much each fact in the report pushed the prediction toward a level or away from it.",
			},
		],
		where: [
			{
				label: "ADRs",
				to: "/adr",
				note: "Open any report. The Prediction tab shows the level and the reasons for it.",
			},
		],
		levels: CAUSALITY_LEVELS.map((level) => level.value),
	},
	{
		id: "review",
		stage: "Step 4",
		icon: "i-lucide-clipboard-check",
		title: "People review the prediction",
		story:
			"A reviewer reads the report and the reasons. The reviewer approves the prediction, or proposes a different level and writes why. Each reviewer votes once. The list tells you which reports still need your review. When an edit changes what the model reads, the model predicts again, and the reviews start again.",
		definitions: [
			{
				term: "Approved",
				text: "A prediction is approved when more reviewers approve it than reject it. A tie counts as not approved.",
			},
		],
		where: [
			{
				label: "ADRs",
				to: "/adr",
				note: "Filter the list by review status. Use the row menu to add or change your review.",
			},
		],
	},
	{
		id: "communicate",
		stage: "Step 5",
		icon: "i-lucide-message-square-text",
		title: "The health facility hears back",
		story:
			"After review, MediLinda can send text messages to the phone numbers of the facility that reported the case. A certain, approved prediction becomes an individual alert. A report the model could not classify becomes a request for more information. The facility can then follow up with the patient.",
		definitions: [],
		where: [
			{
				label: "Individual alerts",
				to: "/communication/individual-alerts",
				note: "Alerts for approved reports with a certain level, and the ones already sent.",
			},
			{
				label: "Additional info requests",
				to: "/communication/additional-information-requests",
				note: "Requests for more facts about reports the model could not classify.",
			},
		],
	},
	{
		id: "learn",
		stage: "Step 6",
		icon: "i-lucide-chart-column-big",
		title: "The record stays, and the picture grows",
		story:
			"Every change to a report is kept. You can see who changed what, and when. A deleted report can be restored. Over time, the reports show which medicines, which facilities and which levels need attention.",
		definitions: [],
		where: [
			{
				label: "Dashboard",
				to: "/dashboard",
				note: "Charts of reviewed and unreviewed reports, levels, approvals and the facilities that report most.",
			},
			{
				label: "Recently deleted",
				to: "/adr/deleted",
				note: "Deleted reports, with a button to restore each one.",
			},
		],
	},
];
