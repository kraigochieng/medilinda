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

## PR 4: the case sampler

- Added `case_sampler.py` (`sample_case`) and `sampler_assumptions.py` (every number that no source gives, in one place).
- Causal order: patient, history, regimen, event and its latent cause, timeline, follow-up (dechallenge, rechallenge), labs, grading, then missing information. The sampler does not import the WHO-UMC rules; a test checks this.
- The latent "drug related" variable (70%, assumption) is an upstream cause. It is kept in `SampledCase.is_drug_related` for checks and is not a model feature. The level still comes only from `assess`.
- The totals come from `marginals.py`. Tests: gender, severity, seriousness and action taken match the PPB report within 3 points over 4,000 cases.
- First look at the class mix (5,000 cases, seed 1, rules applied): possible 56%, unlikely 17%, likely 14%, unclassified 11%, unclassifiable 1%, **certain 0.8%**. Certain is rare: it needs a definitive lab or eye finding, no other cause, a plausible time and an improved dechallenge. DR-4 accepts this mix.
- Consequence for the next steps: the floor of 100 "certain" cases in the test split (DR-4) needs about 55,000 rows. That is too slow for the grid search. I will state the floor that I reach.
- Assumption changed during the work: the history box is empty as a whole (25%), not field by field.
- Tests: 17 tests. The whole ML suite: 191 passed.

## PR 5: the generated dataset and its validation

- Added `dataset_rows.py` (a case as a flat row, the way back to the report fields, label noise), `data_generation.py` (the command) and `dataset_validation.py` (15 checks and the Markdown report).
- Generated `data_who_umc.csv.gz` (30,000 rows, seed 42, label noise 5%) and a separate diagnostics file. The diagnostics file has the clean rule label, the latent cause and the regimen. Training must never read it. The files are compressed with a fixed header, so the same seed gives the same bytes (checked: two runs gave the same SHA-256).
- Validation: all 15 checks passed. The totals match the PPB report within 3 points. The rule label is a function of the visible fields in all 30,000 rows. The share of moved labels is 4.86% (stated 5%).
- Class mix (rule label): possible 55.6%, unlikely 17.8%, likely 14.3%, unclassified 10.4%, unclassifiable 1.1%, certain 0.8% (244 rows).
- **Finding about label noise:** noise moves labels one step along the scale, and "likely" is far larger than "certain". So noise adds about 107 false "certain" rows and removes about 12. In the final label, 343 rows are "certain" and about 30% of them were "likely" by the rules. Any recall of "certain" must be read with this in mind. The clean label is in the diagnostics file.
- Finding about size: the floor in DR-4 was proposed as 100 "certain" rows in the test split. With 30,000 rows the test split has about 86. I kept 30,000 rows because the grid search time grows with the rows. Stated as a deviation.
- The dataset is not yet used by the training. The existing `data.csv` and `selection.json` are unchanged. PR 6 switches them.
- Tests: 11 tests.

## PR 6a: the training code for the new data

- Added `training_data.py`: it loads the dataset (CSV or gzip), keeps the four levels that the model predicts, and drops the new columns for the feature set "app". It refuses a frame that has a diagnostic column (`TrainingDataLeakError`).
- Added `features/history_features.py` and an `include_history` switch in the pipeline: flags become 1, 0 or -1 (not recorded), labs -1 when not measured, text columns become 0 or 1 columns.
- `ModelSelection` has a `feature_set` ("app" or "full"; default "app", so the old selection file is still valid). The experiment and the training read it.
- `headline_metrics` adds `<split>_recall_certain`.
- The experiment has a command line: `python -m medilinda_ml.experiment --feature-set app --cv-splits 3 --cv-repeats 1 --candidates decision_tree,...`.
- Why two feature sets: the production model must run on what the app sends today ("app"). The new report fields (history, labs) are not in the app (#174). The "full" set shows what the app could add.
- The default data path is now `data_who_umc.csv.gz`. The old `data.csv` stays in the repo for the history and for the experiment test.
- Tests: 14 new tests. The whole ML suite: 213 passed, with MLflow.

## PR 6b: the models on the WHO-UMC data

- Ran the experiment twice on the 30,000-row dataset (26,5xx rows of the four levels): feature set "app" (what the app sends today) and feature set "full" (with the new fields of DR-8). Settings: 3-fold cross-validation, one repeat, six candidates (decision tree, AdaBoost, logistic regression, random forest, gradient boosting, naive Bayes). I left out the SVM and the k-nearest-neighbours candidates: their cost grows with the square of the rows. This is a deviation from the earlier experiment (5-fold, three repeats, eight candidates).
- **"app" set:** the winner is gradient boosting with 3 features. Cross-validation weighted F1 0.658, validation 0.654. A model that always predicts the most common level scores 0.464.
- **"full" set:** the winner is gradient boosting with 45 features. Cross-validation 0.848, validation 0.832.
- Held-out test (6,641 rows; 57 are "certain" by the rules), against the clean rule label: "app" weighted F1 0.675, recall of "certain" 0.16; "full" weighted F1 0.879, recall of "certain" 1.00 (57 of 57). The "full" model predicts "certain" 108 times, and 57 are right (precision 0.53). The "app" model predicts "certain" 651 times, and 9 are right (precision 0.014).
- Without the date features the "full" model scores 0.810 (clean label), and recall of "unlikely" falls from 0.81 to 0.45. So the dates carry real information (the time rule), not only a shortcut.
- Label noise: against the clean label the "full" model keeps 0.879 to 0.887 at noise 0%, 5% and 10%. Against the noisy label it falls from 0.887 to 0.798. So the noise lowers the measured score, not the model.
- **Production model:** I trained the "app" model and saved it as the new `LATEST` (with its golden file). It runs on what the app sends today. **It is weak: it over-predicts "certain". Do not deploy it before you read `docs/model-results.md`.** The old model stays in `server/models/`. To restore it, put its folder name in `server/models/LATEST`.
- The "full" model is not saved as a version, because the app does not send its fields (issue #174). The selection is in `selection_full.json`. To train it, copy it over `selection.json` and run the training.
- The scores show how well a model learns the generator. They do not show clinical accuracy.
- Tests: 3 new tests. The whole suite: 526 passed.

## PR 7: the documents

- The About page now says what the data is: synthetic, 30,000 reports, built by a sampler in causal order from two PPB quarterly reports and published TB facts; the level is the output of rules; the class mix and the label noise; and that the model in the app predicts poorly with today's fields while a model with the new fields scores much higher.
- The Prediction tab has a line: "This model learned from 30,000 synthetic reports about 4 TB medicines. The reports are not real patients." with a link to the scope section. The numbers come from `client/app/utils/model-facts.ts`.
- Removed the old sentence "the generator sets the level first". It is no longer true.
- The README of `medilinda_ml` describes the data command, the feature sets, the experiment options, the training, the golden file and the results report.
- Tests: client 345 passed.
- Not done: the root README (issue #111).
