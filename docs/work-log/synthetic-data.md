# Work log: the synthetic data (issue #164)

One entry for each pull request. The entries are written during the work, in order.

## PR 1: the WHO-UMC rules

- Added `case_facts.py` (the six facts and the six levels) and `who_umc.py` (`assess`, a pure function).
- Rule order: cannot be judged, more data needed, unknown time, improbable time, plausible other cause, negative rechallenge (DR-5), other explanation not none, no improvement on withdrawal, then certain or likely.
- Assumptions of the run (not in WHO-UMC): (1) an unknown time gives "unclassified"; (2) no improvement after withdrawal gives "possible"; (3) the time relationship has the extra value "reasonable", because WHO-UMC says "plausible" for certain and "reasonable" for likely and possible.
- Tests: 18 tests, one for each row of the example table in #164 and one for each assumption.

## PR 2: the mapping from the yellow form to the facts

- Added `report_fields.py` (the typed fields of a report, with the DR-8 fields), `reaction_knowledge.py` (reaction categories, time windows, drug-to-reaction table, lab limits) and `yellow_form_mapping.py` (`facts_from_report`, pure).
- Added `docs/yellow-form-mapping.md` with the mapping table, the other causes, and the time windows.
- Assumptions of the run: the time windows for neuropathy, optic, gastrointestinal and joint reactions have no source number; the count rule for other causes (one possible, two plausible) is the project's reading; onset more than 14 days after the stop is improbable.
- Tests: 23 tests for the mapping. With PR 1, 41 tests pass.

## PR 3: the PPB report totals

- Added `marginals.py`: the Q3 FY2025/26 totals (age group, gender, pregnancy, allergy, severity, seriousness, action taken, outcome), the TB combination medicines of Q2 and Q3, and the weights of the reaction categories.
- Each distribution is a `CountedDistribution` that refuses counts that do not add up to the total, and names its page.
- How the numbers were checked: the counts sum to n; the printed percent matches for 10 rows; page 7 was compared with the page image. The other pages were not compared with an image.
- Findings: the reports have all patients, mostly not TB patients (DR-9). Liver injury is not among the 25 events of Q3 (skin events lead). The liver and optic counts are my assumptions (30 and 8) and are marked as such. The share of reports with separate drugs (5%) is an assumption (DR-7).
- Mapping choices: "not indicated" and "unknown" severity map to "unknown"; the outcome "fatal" is the form's "death".
- Tests: 34 tests.
