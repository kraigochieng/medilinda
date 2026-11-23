// The section "About this project" on the About page: what the project is, where the
// data comes from, and the thanks. It is data, so a test can check each fact and link.

export interface CreditLink {
	label: string;
	to: string;
}

export interface CreditParagraph {
	id: "project" | "data" | "thanks";
	before: string;
	links: CreditLink[];
	after: string;
}

export const CREDITS_HEADING = "About this project";

export const CREDITS: CreditParagraph[] = [
	{
		id: "project",
		before:
			"MediLinda is a fourth-year project for a Bachelor's degree in Computer Science. It is a student project. It is not a product of a health authority.",
		links: [],
		after: "",
	},
	{
		id: "data",
		before: "The ADR data comes from the",
		links: [{ label: "Pharmacy and Poisons Board", to: "https://web.pharmacyboardkenya.org/" }],
		after: ". The Board did not work on MediLinda.",
	},
	{
		id: "thanks",
		before: "Thanks to",
		links: [
			{ label: "IntelliSOFT Consulting Ltd", to: "https://www.intellisoftkenya.com" },
			{
				label: "Department of Computer Science, University of Nairobi",
				to: "https://computerscience.uonbi.ac.ke/",
			},
		],
		after: ".",
	},
];
