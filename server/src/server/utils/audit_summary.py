"""A few fields from a row's snapshot, enough to say what an entry is about.

The history lists leave out the full snapshots to stay small. Only the fields
named here are shown, so a list never exposes more than it should (for example
a phone number or a patient's details).
"""

from typing import Any

SUMMARY_FIELDS: dict[str, tuple[str, ...]] = {
    "adr": ("patient_name",),
    "causality_assessment_level": (
        "causality_assessment_level_value",
        "ml_model_id",
    ),
    "review": ("approved", "proposed_causality_level", "reason"),
    "sms_message": ("sms_type", "status"),
    "medical_institution": ("name", "mfl_code"),
    "medical_institution_telephone": ("telephone",),
}


def summarize(entity_type: str, snapshot: dict[str, Any] | None) -> dict[str, Any] | None:
    fields = SUMMARY_FIELDS.get(entity_type)
    if not fields or not snapshot:
        return None

    return {name: snapshot[name] for name in fields if name in snapshot}
