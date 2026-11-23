# Sources for the synthetic data (issue #164)

Research date: 2026-11-23. Agents read the sources and reported to the maintainer. A person has not checked each fact against its source. Check a fact before you use it in code or in text.

## 1. The PPB yellow form

| Item | Value |
|---|---|
| Name | ADR Reporting Form (Yellow), "Suspected Adverse Drug Reaction Reporting Form" |
| Form code | FOM001/MIP/PMS/SOP/001 |
| Page | https://web.pharmacyboardkenya.org/download/adr-reporting-form-yellow/ |
| Format | One page, A4, PDF with a text layer |
| Date | Not printed. The PDF metadata says 2020-06-30. The web page says 2022-02-27. Both are file dates, not form versions. |

### Fields, in order

1. **Top block:** report title; the report is on (suspected adverse drug reaction, or therapeutic ineffectiveness); report type (initial, follow up); product category; institution (name, contact, facility code, county).
2. **Patient information:** name or initials; IP/OP number; date of birth or age; address; ward or clinic; gender; known allergy (no, yes with detail); pregnancy status (not applicable, not pregnant, 1st, 2nd, 3rd trimester); weight in kg; height in cm.
3. **Suspected adverse reaction:** date of onset; brief description.
4. **Medical history:** "Other relevant history including pre-existing medical conditions e.g. allergies, smoking, alcohol use, hepatic/ renal dysfunction etc".
5. **Current medicines** (all medicines now in use, including OTC and herbal; tick the suspected one): tick, generic name, brand name, batch or lot number, manufacturer, dose, route, frequency, start date, stop date, indication.
6. **Past medicines** (last 3 months; for a pregnant patient, the 1st trimester): the same columns, without the tick.
7. **Dechallenge and rechallenge:**
   - "Did the reaction resolve after the drug was stopped or when the dose was reduced?" Yes, No, Unknown, N/A.
   - "Did the reaction reappear after the drug was reintroduced?" Yes, No, Unknown, N/A.
8. **Lab investigations:** "Any lab investigations and results".
9. **Grading:** severity (mild, moderate, severe, fatal, unknown); serious (yes, no); reason for seriousness (hospitalization or prolonged hospitalization, disability, congenital anomaly, life threatening, death); action taken (drug withdrawn, dose reduced, dose increased, dose not changed, not applicable, unknown); outcome (recovered, recovered with sequelae, recovering, not recovered, death, unknown).
10. **Any other comment.**
11. **Reporter details:** the first reporter, and the person who submits to the PPB if different (name, cadre, mobile, email, date).
12. **Official use only:** report number, date received, VigiFlow entry number, date committed.

The form has **no causality assessment section**.

### E-reporting (PvERS)

- Portal: https://pv.pharmacyboardkenya.org/
- The public form is at https://pv.pharmacyboardkenya.org/padrs/add. It has fewer fields: reporter, patient, a list of side effects, start date, medicine name, manufacturer, and outcome. It has no dose, route, batch, dechallenge, rechallenge, severity, or lab fields.
- The form for health workers is behind a login. It was not read.

## 2. The WHO-UMC criteria

Source: https://cdn.who.int/media/docs/default-source/medicines/pharmacovigilance/whocausality-assessment.pdf (3 pages). It has no date and no version. The copy on the UMC site needs a login. The WHO copy may differ from the current UMC copy.

Footnote of the table: "All points should be reasonably complied with".

| Category | Criteria (quoted) |
|---|---|
| Certain | Event or laboratory test abnormality, with plausible time relationship to drug intake. Cannot be explained by disease or other drugs. Response to withdrawal plausible (pharmacologically, pathologically). Event definitive pharmacologically or phenomenologically (i.e. an objective and specific medical disorder or a recognised pharmacological phenomenon). Rechallenge satisfactory, if necessary. |
| Probable / Likely | Event or laboratory test abnormality, with reasonable time relationship to drug intake. Unlikely to be attributed to disease or other drugs. Response to withdrawal clinically reasonable. Rechallenge not required. |
| Possible | Event or laboratory test abnormality, with reasonable time relationship to drug intake. Could also be explained by disease or other drugs. Information on drug withdrawal may be lacking or unclear. |
| Unlikely | Event or laboratory test abnormality, with a time to drug intake that makes a relationship improbable (but not impossible). Disease or other drugs provide plausible explanations. |
| Conditional / Unclassified | Event or laboratory test abnormality. More data for proper assessment needed, or additional data under examination. |
| Unassessable / Unclassifiable | Report suggesting an adverse reaction. Cannot be judged because information is insufficient or contradictory. Data cannot be supplemented or verified. |

### Notes of the document

- "Certain" needs the event to be definitive: "any other event is automatically excluded and can never qualify for 'Certain' (even in the case of a positive rechallenge observation)".
- Rechallenge for "certain" is requested "unless the evidence in the report is already convincing without a re-exposure". For "probable", "a rechallenge is not required".
- "Plausible" time relationship means "in sufficient detail a positive argument in support of the view that the drug is causally involved". "Reasonable" is "a more neutral term covering everything that is not unreasonable".
- Procedure: choose "possible" or "probable", test if the criteria fit, and go one step higher or lower.
- Limit: "It is recognised that the semantics of the definitions are critical and that individual judgements may therefore differ." No system "produces a precise and reliable quantitative estimation of relationship likelihood".
- The document does not say how to treat a negative rechallenge. The project must decide this (see #164, open question 2).

## 3. The four first-line TB drugs

Tags: G is a guideline or a society statement. P is a single paper. S is a search summary that nobody read in full. Do not cite an S item before you read the page.

| Topic | Fact | Source | Tag |
|---|---|---|---|
| Liver injury, Kenya | Grades of ALT or AST in multiples of the upper limit: 1.25 to 2.5, 2.6 to 5.0, 5.1 to 10.0, above 10.0. At grade 3 and 4, stop all drugs. | Kenya Integrated Guideline for TB, Leprosy and Lung Disease 2021, p.53 | G |
| Liver injury, Kenya | Stop hepatotoxic drugs if bilirubin is 51 µmol/L or more, or transaminases are above 5 times the upper limit. | same, p.148 | G |
| Liver injury, ATS | ALT above 3 times the upper limit with symptoms or jaundice, or 5 times without symptoms. | https://www.thoracic.org/statements/resources/mtpi/hepatotoxicity-of-antituberculosis-therapy.pdf | G |
| Most hepatotoxic drug | "Pyrazinamide is the most hepatotoxic anti-TB agent". It is dose related and idiosyncratic. | Kenya guideline p.147; ATS | G |
| Rifampicin | Least likely to cause liver cell damage. It can cause cholestatic jaundice. Severe injury "typically within 1 week to 6 weeks of initiation". | Kenya p.147; https://pmc.ncbi.nlm.nih.gov/articles/PMC11019071/ | G |
| Isoniazid | Hepatitis from weeks to months. Median 16 weeks in a study of latent TB treatment. Slow acetylators have more injury (26% against 11%). | ATS | G |
| Isoniazid, nerves | Neuropathy. Give pyridoxine 50 mg a day. | Kenya p.54 to 55 | G |
| Ethambutol | Optic neuritis, dose related. Stop the drug. It "generally improves following cessation" if stopped early. It is not a hepatotoxic drug. | Kenya p.55; https://pmc.ncbi.nlm.nih.gov/articles/PMC12813275 | G, P |
| Ethambutol, dose | Optic neuritis in below 1%, 3%, 5 to 6%, and 18 to 33% at up to 15, 20, 25 and above 35 mg/kg/day. About 10% of cases within 2 months. | https://pmc.ncbi.nlm.nih.gov/articles/PMC8222132/ | P, S |
| Onset of liver injury | Median 19 days (range 10 to 25) in 142 patients in Morocco. | https://pmc.ncbi.nlm.nih.gov/articles/PMC5326068/ | P |
| Onset of liver injury | In a UK cohort, about half within 2 weeks and nearly 90% within 8 weeks. | https://pmc.ncbi.nlm.nih.gov/articles/PMC12813275 | P |
| Severe skin reaction (DRESS) | Median latency 42 days (interquartile range 28 to 71; range 11 to 131). 15 of 1,253 patients. Causes: ethambutol 8, rifampicin 4, pyrazinamide 3. | https://pmc.ncbi.nlm.nih.gov/articles/PMC6267186/ | P |
| Dechallenge | After stopping, the ALT fell below 100 IU/L in a median of 8 days (interquartile range 5 to 13). | https://pmc.ncbi.nlm.nih.gov/articles/PMC11019071/ | G |
| Rechallenge, Kenya | When tests are normal, add one drug every 3 to 4 days. Order: E, H, R, Z. Consider stopping the worst drug for good, often pyrazinamide. | Kenya p.54, p.148 | G |
| Rechallenge, ATS | Rifampicin first, isoniazid after 3 to 7 days. | ATS | G |
| Rechallenge, South Africa | Isoniazid on day 1, rifampicin on day 4, pyrazinamide on day 8 only if needed. | PMC11019071 | G |
| Rechallenge, a cohort | 79 patients. Recurrence: pyrazinamide 9 of 46, rifampicin 2 of 78, isoniazid 2 of 74. | https://pmc.ncbi.nlm.nih.gov/articles/PMC9257779/ | P |
| Other causes | Hepatitis C, alcohol, paracetamol, antiretrovirals (especially nevirapine), co-trimoxazole, hepatitis B. Screen for hepatitis A, B and C. | Kenya p.147; ATS; PMC11019071 | G |
| Self-limited rise | About 20% have an asymptomatic AST rise that resolves on its own. | Kenya p.147 | G |
| Definitive events | Liver injury by lab values. Ethambutol optic neuropathy needs an eye examination. | Kenya; ATS | G |

## 4. Limits

- The onset time and the dose relation are missing for most drug and reaction pairs. Pyrazinamide and ethambutol have the largest gaps.
- The WHO consolidated guidelines and the aDSM pages need a login. They were not read.
- Parts of the Kenya guideline have a broken font. Pages 53 to 55 and 147 to 148 were read as images.
- No Kenya-specific paper on the causes of liver injury was found. TB as a cause of the event is not covered.
- The WHO practical handbook on pharmacovigilance for TB medicines was found but not read for drug facts: https://www.who.int/docs/default-source/documents/tuberculosis/a-practical-handbook-on-the-pharmacovigilance-of-medicines-used-in-the-treatment-of-tuberculosis.pdf?sfvrsn=6e5fc0cf_5
