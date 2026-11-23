"""The totals of the PPB quarterly reports, and the weights that the sampler needs.

Source of the report totals: the Pharmacovigilance Summary Report of the Pharmacy and Poisons Board,
Q3 FY2025/26 (1 January to 31 March 2026), n = 336 reports of suspected adverse drug reactions, and
the Q2 report (1 October to 31 December 2025) for the medicine counts. The OCR text is in
docs/ppb-reports/. Each distribution names its page.

How the numbers were checked: each count sums to its n (a test checks this), and the percent that the
report prints matches the count (a test checks this for the main rows). The counts of page 7 were also
compared with the page image. The other pages were not compared with an image.

The totals are for ALL patients of the report, not for TB patients only (decision DR-9).
"""

from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator


class CountedDistribution(BaseModel):
    """Counts for the categories of one field, with the total n and the page of the source."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    counts: dict[str, int]
    total: int
    source: str

    @model_validator(mode="after")
    def counts_sum_to_total(self) -> "CountedDistribution":
        """Refuse a distribution whose counts do not add up to its total."""
        if sum(self.counts.values()) != self.total:
            raise ValueError(f"{self.name}: the counts sum to {sum(self.counts.values())}, not {self.total}")
        return self


def proportions(*, distribution: CountedDistribution) -> dict[str, float]:
    """Return the share of each category. The shares sum to one."""
    return {category: count / distribution.total for category, count in distribution.counts.items()}


Q3_SOURCE: Final[str] = "PPB Pharmacovigilance Summary Report Q3 FY2025/26 (Jan to Mar 2026)"

AGE_GROUP = CountedDistribution(
    name="age_group",
    counts={"neonate": 6, "infant": 3, "child": 12, "adolescent": 7, "adult": 260, "elderly": 48},
    total=336,
    source=f"{Q3_SOURCE}, page 3",
)

GENDER = CountedDistribution(
    name="gender", counts={"female": 208, "male": 128}, total=336, source=f"{Q3_SOURCE}, page 4"
)

# Among the 208 female patients only.
PREGNANCY_STATUS_OF_FEMALES = CountedDistribution(
    name="pregnancy_status_of_females",
    counts={
        "not_pregnant": 125,
        "not_applicable": 41,
        "not_indicated": 29,
        "third_trimester": 8,
        "second_trimester": 4,
        "first_trimester": 1,
    },
    total=208,
    source=f"{Q3_SOURCE}, page 4",
)

KNOWN_ALLERGY = CountedDistribution(
    name="known_allergy", counts={"no": 257, "yes": 23, "not_indicated": 56}, total=336, source=f"{Q3_SOURCE}, page 4"
)

# The report prints 11 "not indicated" and 1 "unknown". Both map to the form answer "unknown".
SEVERITY = CountedDistribution(
    name="severity",
    counts={"mild": 144, "moderate": 125, "severe": 49, "fatal": 6, "unknown": 12},
    total=336,
    source=f"{Q3_SOURCE}, page 6",
)

IS_SERIOUS = CountedDistribution(
    name="is_serious", counts={"no": 270, "yes": 66}, total=336, source=f"{Q3_SOURCE}, page 7"
)

# Among the 66 serious reports only.
CRITERIA_FOR_SERIOUSNESS = CountedDistribution(
    name="criteria_for_seriousness",
    counts={"hospitalization": 34, "life_threatening": 20, "disability": 7, "death": 5},
    total=66,
    source=f"{Q3_SOURCE}, page 7",
)

ACTION_TAKEN = CountedDistribution(
    name="action_taken",
    counts={
        "drug_withdrawn": 206,
        "dose_not_changed": 91,
        "not_applicable": 26,
        "dose_reduced": 6,
        "unknown": 4,
        "dose_increased": 3,
    },
    total=336,
    source=f"{Q3_SOURCE}, page 7",
)

# The report prints "not indicated" (3) and "not recovered, ongoing" (1). They map to "unknown" and
# "not_recovered". The yellow form has no "fatal" outcome word: it says "death".
OUTCOME = CountedDistribution(
    name="outcome",
    counts={"recovering": 127, "recovered": 80, "not_recovered": 64, "unknown": 58, "death": 7},
    total=336,
    source=f"{Q3_SOURCE}, page 8",
)

# The TB combination medicines among the suspected medicines of the Q2 and Q3 reports (all patients).
# Isoniazid with rifapentine is left out: the project has no rifapentine column.
TB_COMBINATION_MENTIONS = CountedDistribution(
    name="tb_combination_mentions",
    counts={"rhze": 89 + 64, "rhz": 5, "rh": 5 + 6},
    total=89 + 64 + 5 + 5 + 6,
    source="PPB Q2 FY2025/26 report (suspected medicines, n=324) and Q3 report (page 5, n=352): "
    "RHZE 89 and 64, RHZ 5, RH 5 and 6",
)

# Assumption (decision DR-7): the share of reports with the four drugs as separate medicines.
# The reports list no separate TB drug among their top medicines, so this number has no source.
SEPARATE_DRUGS_SHARE: Final[float] = 0.05

# The top adverse events of Q3 (all patients, 563 events), grouped into the categories of
# reaction_knowledge.py. The liver and optic counts are ASSUMPTIONS: the TB drugs are known to cause
# them, but neither is among the 25 events that the report lists.
Q3_EVENT_COUNTS_BY_CATEGORY: Final[dict[str, int]] = {
    "skin": 55 + 51 + 9 + 7 + 6,  # itching, rash, skin hyperpigmentation, angioedema, Stevens-Johnson
    "gastrointestinal": 13 + 13 + 6 + 6,  # nausea, vomiting, diarrhea, mouth sores
    "neuropathy": 8,  # peripheral neuropathy
    "joint": 10,  # arthralgia
    "nonspecific": 24 + 15 + 9 + 9 + 7 + 8 + 8 + 7,  # headache, dizziness, fatigue, shivering, malaise, palpitation, myalgia, cough
}
ASSUMED_EVENT_COUNTS_BY_CATEGORY: Final[dict[str, int]] = {"liver": 30, "optic": 8}

REACTION_CATEGORY_COUNTS = CountedDistribution(
    name="reaction_category",
    counts={**Q3_EVENT_COUNTS_BY_CATEGORY, **ASSUMED_EVENT_COUNTS_BY_CATEGORY},
    total=sum(Q3_EVENT_COUNTS_BY_CATEGORY.values()) + sum(ASSUMED_EVENT_COUNTS_BY_CATEGORY.values()),
    source=f"{Q3_SOURCE}, page 5 (top events); the liver and optic counts are assumptions",
)

ALL_DISTRIBUTIONS: Final[list[CountedDistribution]] = [
    AGE_GROUP,
    GENDER,
    PREGNANCY_STATUS_OF_FEMALES,
    KNOWN_ALLERGY,
    SEVERITY,
    IS_SERIOUS,
    CRITERIA_FOR_SERIOUSNESS,
    ACTION_TAKEN,
    OUTCOME,
    TB_COMBINATION_MENTIONS,
    REACTION_CATEGORY_COUNTS,
]
