from fastapi import status


class MedilindaError(Exception):
    """Base exception for all application-specific errors."""

    def __init__(
        self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RepositoryError(MedilindaError):
    """Base exception for repository-layer errors."""

    def __init__(
        self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(message, status_code)


class ResourceNotFoundError(RepositoryError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class DatabaseError(RepositoryError):
    """Raised for general database-level errors."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServiceError(MedilindaError):
    """Base exception for service-layer errors."""

    def __init__(
        self,
        message: str = "Service not found",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        super().__init__(message, status_code)


class UserAlreadyExistsError(ServiceError):
    def __init__(
        self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(message, status_code)
