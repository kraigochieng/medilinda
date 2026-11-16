from pathlib import Path


class MedilindaMlError(Exception):
    """The base of every error that the medilinda_ml package raises."""


class ModelStoreError(MedilindaMlError):
    """The base of every error that the model store raises."""


class ModelNotFoundError(ModelStoreError):
    """The requested model version does not exist in the store."""

    def __init__(self, *, version: str) -> None:
        super().__init__(f"Model version '{version}' was not found.")
        self.version: str = version


class ModelIntegrityError(ModelStoreError):
    """A file of a model version does not match its manifest."""

    def __init__(self, *, version: str, file_name: str, reason: str) -> None:
        super().__init__(
            f"Model version '{version}' failed the integrity check on "
            f"'{file_name}': {reason}."
        )
        self.version: str = version
        self.file_name: str = file_name
        self.reason: str = reason


class ModelVersionExistsError(ModelStoreError):
    """A model version with the same name is already in the store."""

    def __init__(self, *, version: str) -> None:
        super().__init__(f"Model version '{version}' already exists.")
        self.version: str = version


class ModelVersionNameError(ModelStoreError):
    """The inputs of a model version name are not valid."""


class UnknownCandidateError(MedilindaMlError):
    """No estimator candidate has the requested name."""

    def __init__(self, *, name: str, known: list[str]) -> None:
        super().__init__(f"No candidate is named '{name}'. The known names are {known}.")
        self.name: str = name
        self.known: list[str] = known


class SelectionError(MedilindaMlError):
    """The base of every error that the model selection file raises."""


class SelectionNotFoundError(SelectionError):
    """The selection file does not exist. Run the experiment to make it."""

    def __init__(self, *, path: Path) -> None:
        super().__init__(
            f"The selection file '{path}' does not exist. Run the experiment first."
        )
        self.path: Path = path


class SelectionInvalidError(SelectionError):
    """The selection file is not valid JSON or does not match the schema."""

    def __init__(self, *, path: Path, reason: str) -> None:
        super().__init__(f"The selection file '{path}' is not valid: {reason}")
        self.path: Path = path
        self.reason: str = reason


class SelectionDataMismatchError(SelectionError):
    """The data file differs from the data that the experiment used."""

    def __init__(self, *, data_path: Path, expected: str, actual: str) -> None:
        super().__init__(
            f"The data file '{data_path}' has hash {actual[:12]}, but the selection "
            f"was made with hash {expected[:12]}. Run the experiment again."
        )
        self.data_path: Path = data_path
        self.expected: str = expected
        self.actual: str = actual
