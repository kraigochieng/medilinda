"""The WHO-UMC causality rules as one pure function.

The criteria are quoted in docs/research/synthetic-data-sources.md. Where the WHO-UMC
text is silent, this module follows the decisions of the project (issue #164):

- DR-5: a negative rechallenge caps the level at "possible".
- A time relationship that is "unknown" cannot be judged yet, so the level is "unclassified".
- No improvement after withdrawal, with no other explanation, gives "possible".
  This is a reading of the project, not a WHO-UMC rule.
"""

from medilinda_ml.case_facts import (
    CaseFacts,
    CausalityLevel,
    Dechallenge,
    Information,
    OtherExplanation,
    Rechallenge,
    TimeRelationship,
)


def assess(*, facts: CaseFacts) -> CausalityLevel:
    """Return the WHO-UMC level of the facts. Pure: the same facts always give the same level."""
    if facts.information is Information.CANNOT_BE_JUDGED:
        return CausalityLevel.UNCLASSIFIABLE
    if facts.information is Information.MORE_DATA_NEEDED:
        return CausalityLevel.UNCLASSIFIED
    if facts.time_relationship is TimeRelationship.UNKNOWN:
        return CausalityLevel.UNCLASSIFIED
    if facts.time_relationship is TimeRelationship.IMPROBABLE:
        return CausalityLevel.UNLIKELY
    if facts.other_explanation is OtherExplanation.PLAUSIBLE:
        return CausalityLevel.UNLIKELY
    if facts.rechallenge is Rechallenge.NEGATIVE:
        return CausalityLevel.POSSIBLE
    if facts.other_explanation is not OtherExplanation.NONE:
        return CausalityLevel.POSSIBLE
    if facts.dechallenge is not Dechallenge.IMPROVED:
        return CausalityLevel.POSSIBLE
    if _is_certain(facts=facts):
        return CausalityLevel.CERTAIN
    return CausalityLevel.LIKELY


def _is_certain(*, facts: CaseFacts) -> bool:
    """Return True when every criterion of "certain" holds, given that no other explanation exists."""
    return (
        facts.time_relationship is TimeRelationship.PLAUSIBLE
        and facts.event_definitive
        and facts.rechallenge is not Rechallenge.NEGATIVE
    )
