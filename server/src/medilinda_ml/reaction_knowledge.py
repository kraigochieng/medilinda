"""What is known about the reactions of the four first-line TB drugs.

Pure data and pure functions. Each table row has a source tag:

- guideline: the Kenya Integrated Guideline 2021, ATS 2006, or a consensus statement.
- paper: a single paper.
- assumption: no source gave a number. The project chose the value. State it as a limit.

The sources are in docs/research/synthetic-data-sources.md.
"""

from enum import StrEnum
from typing import Final

from medilinda_ml.report_fields import DrugName
from pydantic import BaseModel, ConfigDict


class ReactionCategory(StrEnum):
    """A group of reaction terms that share a time window and a set of other causes."""

    LIVER = "liver"
    SKIN = "skin"
    NEUROPATHY = "neuropathy"
    OPTIC = "optic"
    GASTROINTESTINAL = "gastrointestinal"
    JOINT = "joint"
    NONSPECIFIC = "nonspecific"


class TimeWindow(BaseModel):
    """Days from the start of the drug: the plausible window and the end of the reasonable window."""

    model_config = ConfigDict(frozen=True)

    plausible_from_days: int
    plausible_to_days: int
    reasonable_to_days: int
    source: str


# The category of each reaction term. A term outside this table is "nonspecific".
REACTION_CATEGORY_BY_TERM: Final[dict[str, ReactionCategory]] = {
    "jaundice": ReactionCategory.LIVER,
    "hepatotoxicity": ReactionCategory.LIVER,
    "hepatitis": ReactionCategory.LIVER,
    "raised liver enzymes": ReactionCategory.LIVER,
    "rash": ReactionCategory.SKIN,
    "itching": ReactionCategory.SKIN,
    "tingling": ReactionCategory.NEUROPATHY,
    "numbness": ReactionCategory.NEUROPATHY,
    "blurred vision": ReactionCategory.OPTIC,
    "eye pain": ReactionCategory.OPTIC,
    "color blindness": ReactionCategory.OPTIC,
    "optic neuritis": ReactionCategory.OPTIC,
    "nausea": ReactionCategory.GASTROINTESTINAL,
    "vomiting": ReactionCategory.GASTROINTESTINAL,
    "loss of appetite": ReactionCategory.GASTROINTESTINAL,
    "abdominal pain": ReactionCategory.GASTROINTESTINAL,
    "joint pain": ReactionCategory.JOINT,
}

# The categories that each drug is known to cause. Nonspecific terms are allowed for every drug.
KNOWN_CATEGORIES_BY_DRUG: Final[dict[DrugName, frozenset[ReactionCategory]]] = {
    DrugName.RIFAMPICIN: frozenset({ReactionCategory.LIVER, ReactionCategory.SKIN, ReactionCategory.GASTROINTESTINAL}),
    DrugName.ISONIAZID: frozenset({ReactionCategory.LIVER, ReactionCategory.NEUROPATHY, ReactionCategory.SKIN, ReactionCategory.GASTROINTESTINAL}),
    DrugName.PYRAZINAMIDE: frozenset({ReactionCategory.LIVER, ReactionCategory.JOINT, ReactionCategory.GASTROINTESTINAL, ReactionCategory.SKIN}),
    DrugName.ETHAMBUTOL: frozenset({ReactionCategory.OPTIC, ReactionCategory.SKIN, ReactionCategory.GASTROINTESTINAL}),
}

TIME_WINDOW_BY_CATEGORY: Final[dict[ReactionCategory, TimeWindow]] = {
    ReactionCategory.LIVER: TimeWindow(
        plausible_from_days=7, plausible_to_days=56, reasonable_to_days=180,
        source="paper: median 19 days (10 to 25), about 90% within 8 weeks; guideline: severe injury within 1 to 6 weeks; isoniazid up to months (assumption for the 180 days)",
    ),
    ReactionCategory.SKIN: TimeWindow(
        plausible_from_days=14, plausible_to_days=84, reasonable_to_days=180,
        source="paper: DRESS median 42 days (28 to 71), range 11 to 131 (assumption for the 180 days)",
    ),
    ReactionCategory.NEUROPATHY: TimeWindow(
        plausible_from_days=28, plausible_to_days=270, reasonable_to_days=365,
        source="assumption: the sources say weeks to months and give no numbers",
    ),
    ReactionCategory.OPTIC: TimeWindow(
        plausible_from_days=14, plausible_to_days=240, reasonable_to_days=365,
        source="assumption: dose related, mostly months; one paper (search summary) says about 10% within 2 months",
    ),
    ReactionCategory.GASTROINTESTINAL: TimeWindow(
        plausible_from_days=1, plausible_to_days=60, reasonable_to_days=120,
        source="assumption: early in treatment",
    ),
    ReactionCategory.JOINT: TimeWindow(
        plausible_from_days=1, plausible_to_days=60, reasonable_to_days=120,
        source="assumption: early in treatment",
    ),
    ReactionCategory.NONSPECIFIC: TimeWindow(
        plausible_from_days=1, plausible_to_days=60, reasonable_to_days=120,
        source="assumption: a nonspecific term is never better than reasonable",
    ),
}

# ALT and bilirubin limits for a definitive liver event. Source: Kenya guideline p.148 (5 times the
# upper limit of ALT or AST, or bilirubin 51 micromoles per litre or more).
DEFINITIVE_ALT_MULTIPLE: Final[float] = 5.0
DEFINITIVE_BILIRUBIN_UMOL_PER_L: Final[float] = 51.0


def category_of(*, term: str) -> ReactionCategory:
    """Return the category of a reaction term. An unknown term is nonspecific."""
    return REACTION_CATEGORY_BY_TERM.get(term.strip().lower(), ReactionCategory.NONSPECIFIC)


def categories_of(*, terms: list[str]) -> frozenset[ReactionCategory]:
    """Return the set of categories of the reaction terms."""
    return frozenset(category_of(term=term) for term in terms)
