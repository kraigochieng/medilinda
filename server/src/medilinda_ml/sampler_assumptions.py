"""The numbers of the sampler that no source gives. Each one is an ASSUMPTION of the project.

They are in one place so that the About page, the work log and a reviewer can read them all.
Change a number here and the generated data changes. Decisions DR-6, DR-7, DR-8 and DR-9 of
issue #164 explain why the sampler needs them.
"""

from pydantic import BaseModel, ConfigDict


class SamplerAssumptions(BaseModel):
    """Prevalences, probabilities and rates that the sampler uses where no source gave a number."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # The share of events that the drug truly causes. The rest are coincidence or another cause.
    drug_related_share: float = 0.7
    # Of drug-related events, the share whose onset is outside the plausible window.
    outside_window_share: float = 0.1

    # History (DR-8). No source gives these numbers for TB patients in Kenya.
    alcohol_use: float = 0.15
    hepatic_dysfunction: float = 0.03
    renal_dysfunction: float = 0.04
    hiv_positive: float = 0.25
    hepatitis_b_or_c: float = 0.03
    # The share of reports whose history box (section 4 of the form, one free-text box) is empty.
    history_not_recorded: float = 0.25
    # The share of reports whose list of other medicines (sections 5 and 6) is empty.
    medicines_not_recorded: float = 0.10

    # Antiretroviral type among patients with HIV.
    dolutegravir_share: float = 0.85
    nnrti_share: float = 0.10
    cotrimoxazole_with_hiv: float = 0.8
    cotrimoxazole_without_hiv: float = 0.05
    other_hepatotoxic_medicine: float = 0.05

    # Follow-up (DR-6 and the form).
    rechallenge_done_after_withdrawal: float = 0.10
    dechallenge_improved_if_related: float = 0.85
    dechallenge_improved_if_unrelated: float = 0.30
    rechallenge_positive_if_related: float = 0.70
    answer_unknown: float = 0.10

    # Labs.
    alt_measured_if_liver: float = 0.80
    bilirubin_measured_if_liver: float = 0.60
    alt_measured_other: float = 0.20
    bilirubin_measured_other: float = 0.15
    exam_done_if_optic: float = 0.60
    exam_abnormal_if_related: float = 0.85
    exam_abnormal_if_unrelated: float = 0.30

    # Missing information in the report.
    onset_missing: float = 0.08
    start_date_missing: float = 0.05
    no_suspected_drug_ticked: float = 0.01

    # The reaction is of a category that a suspected drug is known to cause.
    known_category_share: float = 0.85

    # Body size of TB patients. BMI is lower than in the general population.
    adult_bmi_mean: float = 19.5
    adult_bmi_deviation: float = 3.0


DEFAULT_ASSUMPTIONS = SamplerAssumptions()
