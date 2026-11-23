"""The facts of one report that the WHO-UMC causality rules read.

The WHO-UMC criteria (see docs/research/synthetic-data-sources.md) look at six things:
the time relationship, other explanations, the response to withdrawal, the rechallenge,
whether the event is definitive, and whether the information is enough.
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class CausalityLevel(StrEnum):
    """The six WHO-UMC levels, named as the data, the server and the client name them."""

    CERTAIN = "certain"
    LIKELY = "likely"
    POSSIBLE = "possible"
    UNLIKELY = "unlikely"
    UNCLASSIFIED = "unclassified"
    UNCLASSIFIABLE = "unclassifiable"


class TimeRelationship(StrEnum):
    """How the time from drug intake to the event fits a causal link."""

    PLAUSIBLE = "plausible"  # a positive argument supports a causal link
    REASONABLE = "reasonable"  # not unreasonable: the neutral term of WHO-UMC
    IMPROBABLE = "improbable"  # makes a link improbable, but not impossible
    UNKNOWN = "unknown"


class OtherExplanation(StrEnum):
    """How well a disease or another drug explains the event."""

    NONE = "none"  # the event cannot be explained by disease or other drugs
    POSSIBLE = "possible"  # the event could also be explained by them
    PLAUSIBLE = "plausible"  # they give a more likely explanation
    UNKNOWN = "unknown"


class Dechallenge(StrEnum):
    """What happened when the suspected drug was stopped."""

    IMPROVED = "improved"
    NOT_IMPROVED = "not_improved"
    NOT_DONE = "not_done"
    UNKNOWN = "unknown"


class Rechallenge(StrEnum):
    """What happened when the suspected drug was given again."""

    POSITIVE = "positive"  # the event came back
    NEGATIVE = "negative"  # the event did not come back
    NOT_DONE = "not_done"
    UNKNOWN = "unknown"


class Information(StrEnum):
    """Whether the report holds enough information to judge."""

    SUFFICIENT = "sufficient"
    MORE_DATA_NEEDED = "more_data_needed"  # more data is wanted or under examination
    CANNOT_BE_JUDGED = "cannot_be_judged"  # insufficient or contradictory, and cannot be completed


class CaseFacts(BaseModel):
    """The six facts that decide the WHO-UMC level. A value outside the enums is refused."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    time_relationship: TimeRelationship
    other_explanation: OtherExplanation
    dechallenge: Dechallenge
    rechallenge: Rechallenge
    event_definitive: bool  # an objective and specific medical disorder, or a recognised pharmacological phenomenon
    information: Information
