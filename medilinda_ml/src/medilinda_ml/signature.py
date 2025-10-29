from mlflow.models import ModelSignature
from mlflow.types import DataType
from mlflow.types.schema import ColSpec, Schema

# input_schema = Schema(
#     [
#         # Institution Details
#         ColSpec(DataType.string, "medical_institution_id"),
#         # Personal Details
#         ColSpec(DataType.string, "patient_name"),
#         ColSpec(DataType.string, "inpatient_or_outpatient_number", required=False),
#         ColSpec(DataType.string, "patient_date_of_birth", required=False),
#         ColSpec(DataType.long, "patient_age", required=False),
#         ColSpec(DataType.string, "patient_address", required=False),
#         ColSpec(DataType.string, "ward_or_clinic", required=False),
#         ColSpec(DataType.string, "patient_gender"),
#         ColSpec(DataType.string, "known_allergy"),
#         ColSpec(DataType.string, "pregnancy_status"),
#         ColSpec(DataType.double, "patient_weight_kg", required=False),
#         ColSpec(DataType.double, "patient_height_cm", required=False),
#         # Suspected Adverse Reaction
#         ColSpec(DataType.string, "date_of_onset_of_reaction", required=False),
#         ColSpec(DataType.string, "description_of_reaction", required=False),
#         # --- Medicine Columns ---
#         # Rifampicin
#         ColSpec(DataType.boolean, "rifampicin_suspected", required=False),
#         ColSpec(DataType.string, "rifampicin_start_date", required=False),
#         ColSpec(DataType.string, "rifampicin_stop_date", required=False),
#         ColSpec(DataType.long, "rifampicin_dose_amount", required=False),
#         ColSpec(DataType.long, "rifampicin_frequency_number", required=False),
#         ColSpec(DataType.string, "rifampicin_route", required=False),
#         ColSpec(DataType.string, "rifampicin_batch_no", required=False),
#         ColSpec(DataType.string, "rifampicin_manufacturer", required=False),
#         # Isoniazid
#         ColSpec(DataType.boolean, "isoniazid_suspected", required=False),
#         ColSpec(DataType.string, "isoniazid_start_date", required=False),
#         ColSpec(DataType.string, "isoniazid_stop_date", required=False),
#         ColSpec(DataType.long, "isoniazid_dose_amount", required=False),
#         ColSpec(DataType.long, "isoniazid_frequency_number", required=False),
#         ColSpec(DataType.string, "isoniazid_route", required=False),
#         ColSpec(DataType.string, "isoniazid_batch_no", required=False),
#         ColSpec(DataType.string, "isoniazid_manufacturer", required=False),
#         # Pyrazinamide
#         ColSpec(DataType.boolean, "pyrazinamide_suspected", required=False),
#         ColSpec(DataType.string, "pyrazinamide_start_date", required=False),
#         ColSpec(DataType.string, "pyrazinamide_stop_date", required=False),
#         ColSpec(DataType.long, "pyrazinamide_dose_amount", required=False),
#         ColSpec(DataType.long, "pyrazinamide_frequency_number", required=False),
#         ColSpec(DataType.string, "pyrazinamide_route", required=False),
#         ColSpec(DataType.string, "pyrazinamide_batch_no", required=False),
#         ColSpec(DataType.string, "pyrazinamide_manufacturer", required=False),
#         # Ethambutol
#         ColSpec(DataType.boolean, "ethambutol_suspected", required=False),
#         ColSpec(DataType.string, "ethambutol_start_date", required=False),
#         ColSpec(DataType.string, "ethambutol_stop_date", required=False),
#         ColSpec(DataType.long, "ethambutol_dose_amount", required=False),
#         ColSpec(DataType.long, "ethambutol_frequency_number", required=False),
#         ColSpec(DataType.string, "ethambutol_route", required=False),
#         ColSpec(DataType.string, "ethambutol_batch_no", required=False),
#         ColSpec(DataType.string, "ethambutol_manufacturer", required=False),
#         # Rechallenge/Dechallenge
#         ColSpec(DataType.string, "rechallenge"),
#         ColSpec(DataType.string, "dechallenge"),
#         # Grading of Reaction/Event
#         ColSpec(DataType.string, "severity"),
#         ColSpec(DataType.string, "is_serious"),
#         ColSpec(DataType.string, "criteria_for_seriousness"),
#         ColSpec(DataType.string, "action_taken"),
#         ColSpec(DataType.string, "outcome"),
#         ColSpec(DataType.string, "comments", required=False),
#     ]
# )


input_schema = Schema(
    [
        # Institution Details
        ColSpec(DataType.string, "medical_institution_id"),
        # Personal Details
        ColSpec(DataType.string, "patient_name"),
        ColSpec(DataType.string, "inpatient_or_outpatient_number", required=False),
        ColSpec(DataType.string, "patient_date_of_birth", required=False),
        ColSpec(DataType.double, "patient_age", required=False),
        ColSpec(DataType.string, "patient_address", required=False),
        ColSpec(DataType.string, "ward_or_clinic", required=False),
        ColSpec(DataType.string, "patient_gender"),
        ColSpec(DataType.string, "known_allergy"),
        ColSpec(DataType.string, "pregnancy_status"),
        ColSpec(DataType.double, "patient_weight_kg", required=False),
        ColSpec(DataType.double, "patient_height_cm", required=False),
        # Suspected Adverse Reaction
        ColSpec(DataType.string, "date_of_onset_of_reaction", required=False),
        ColSpec(DataType.string, "description_of_reaction", required=False),
        # --- Medicine Columns ---
        # Rifampicin
        ColSpec(DataType.boolean, "rifampicin_suspected", required=False),
        ColSpec(DataType.string, "rifampicin_start_date", required=False),
        ColSpec(DataType.string, "rifampicin_stop_date", required=False),
        ColSpec(DataType.double, "rifampicin_dose_amount", required=False),
        ColSpec(DataType.double, "rifampicin_frequency_number", required=False),
        ColSpec(DataType.string, "rifampicin_route", required=False),
        ColSpec(DataType.string, "rifampicin_batch_no", required=False),
        ColSpec(DataType.string, "rifampicin_manufacturer", required=False),
        # Isoniazid
        ColSpec(DataType.boolean, "isoniazid_suspected", required=False),
        ColSpec(DataType.string, "isoniazid_start_date", required=False),
        ColSpec(DataType.string, "isoniazid_stop_date", required=False),
        ColSpec(DataType.double, "isoniazid_dose_amount", required=False),
        ColSpec(DataType.double, "isoniazid_frequency_number", required=False),
        ColSpec(DataType.string, "isoniazid_route", required=False),
        ColSpec(DataType.string, "isoniazid_batch_no", required=False),
        ColSpec(DataType.string, "isoniazid_manufacturer", required=False),
        # Pyrazinamide
        ColSpec(DataType.boolean, "pyrazinamide_suspected", required=False),
        ColSpec(DataType.string, "pyrazinamide_start_date", required=False),
        ColSpec(DataType.string, "pyrazinamide_stop_date", required=False),
        ColSpec(DataType.double, "pyrazinamide_dose_amount", required=False),
        ColSpec(DataType.double, "pyrazinamide_frequency_number", required=False),
        ColSpec(DataType.string, "pyrazinamide_route", required=False),
        ColSpec(DataType.string, "pyrazinamide_batch_no", required=False),
        ColSpec(DataType.string, "pyrazinamide_manufacturer", required=False),
        # Ethambutol
        ColSpec(DataType.boolean, "ethambutol_suspected", required=False),
        ColSpec(DataType.string, "ethambutol_start_date", required=False),
        ColSpec(DataType.string, "ethambutol_stop_date", required=False),
        ColSpec(DataType.double, "ethambutol_dose_amount", required=False),
        ColSpec(DataType.double, "ethambutol_frequency_number", required=False),
        ColSpec(DataType.string, "ethambutol_route", required=False),
        ColSpec(DataType.string, "ethambutol_batch_no", required=False),
        ColSpec(DataType.string, "ethambutol_manufacturer", required=False),
        # Rechallenge/Dechallenge
        ColSpec(DataType.string, "rechallenge"),
        ColSpec(DataType.string, "dechallenge"),
        # Grading of Reaction/Event
        ColSpec(DataType.string, "severity"),
        ColSpec(DataType.string, "is_serious"),
        ColSpec(DataType.string, "criteria_for_seriousness"),
        ColSpec(DataType.string, "action_taken"),
        ColSpec(DataType.string, "outcome"),
        ColSpec(DataType.string, "comments", required=False),
        # ColSpec(DataType.string, "created_at", required=False),
    ]
)

output_schema = Schema([ColSpec(DataType.long, "prediction")])

signature = ModelSignature(inputs=input_schema, outputs=output_schema)
