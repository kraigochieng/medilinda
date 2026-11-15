import logging
from pathlib import Path

from medilinda_ml.model_store import ModelEnsemble, read_version


def load_model_ensemble(*, models_root: Path, version: str) -> ModelEnsemble:
    """Side effect (disk): load the model, the encoder and the explainer of a version.

    Raise a ModelStoreError when the version is missing or a file fails its hash check.
    """
    ensemble = read_version(root=models_root, version=version)
    logging.info("Loaded model version %s from %s.", ensemble.version, models_root)

    return ensemble
