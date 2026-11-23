# Mapping from the PPB yellow form to the WHO-UMC facts

Code: `server/src/medilinda_ml/yellow_form_mapping.py`, `report_fields.py`, `reaction_knowledge.py`. Decisions: DR-3, DR-7, DR-8 in issue #164. The form is described in `docs/research/synthetic-data-sources.md`.

## Mapping table

| WHO-UMC fact | Yellow form source | Rule |
|---|---|---|
| Time relationship | Section 2 (onset), section 5 (start and stop of each medicine, tick on the suspected one) | Best result over the suspected drugs and the reaction categories. Onset before the start, or more than 14 days after the stop: improbable. Inside the plausible window of the category, and the drug is known to cause that category: plausible. Otherwise, up to the end of the reasonable window: reasonable. A missing date: unknown. |
| Other explanation | Section 4 (history), sections 5 and 6 (other medicines) | Count the other causes for the main reaction category. None, all recorded: none. A factor not recorded and none present: unknown. One: possible. Two or more: plausible. |
| Dechallenge | Section 7, question 1 | Yes: improved. No: not improved. N/A: not done. Unknown: unknown. |
| Rechallenge | Section 7, question 2 | Yes: positive. No: negative. N/A: not done. Unknown: unknown. |
| Event definitive | Section 8 (lab investigations) | Liver reaction with ALT at 5 times the upper limit or more, or bilirubin at 51 micromoles per litre or more. Optic reaction with an abnormal eye exam. Other reactions: not definitive. |
| Information | Sections 2 and 5 | No suspected drug, or no reaction: cannot be judged. No onset date, or no start date of a suspected drug: more data needed. Otherwise: sufficient. |

## Other causes by reaction category

| Category | Factors that count as another cause |
|---|---|
| Liver | hepatitis B or C, alcohol use, hepatic dysfunction, antiretroviral with nevirapine or efavirenz, co-trimoxazole, another hepatotoxic medicine |
| Optic | alcohol use |
| Neuropathy | HIV positive, alcohol use, renal dysfunction |
| Skin | co-trimoxazole, HIV positive, antiretroviral with nevirapine or efavirenz |
| Joint | alcohol use |
| Gastrointestinal | alcohol use, any antiretroviral, co-trimoxazole |
| Nonspecific | HIV positive, hepatitis B or C, alcohol use |

## Time windows (days from the start of the drug)

| Category | Plausible | Reasonable up to | Source |
|---|---|---|---|
| Liver | 7 to 56 | 180 | paper and guideline; the 180 is an assumption |
| Skin | 14 to 84 | 180 | paper (DRESS); the 180 is an assumption |
| Neuropathy | 28 to 270 | 365 | assumption |
| Optic | 14 to 240 | 365 | assumption |
| Gastrointestinal | 1 to 60 | 120 | assumption |
| Joint | 1 to 60 | 120 | assumption |
| Nonspecific | never plausible | 120 | assumption |

## Limits

- The windows marked "assumption" have no source number. A clinician should review them.
- The count rule for other causes (one is possible, two are plausible) is a project reading. WHO-UMC gives no count.
- The form has no field for HIV, hepatitis, or a type of antiretroviral. DR-8 adds them. The app form does not have them yet (issue #174).
- The list of reaction terms and the drug-to-reaction table are short. A term that is not in the list is "nonspecific".
