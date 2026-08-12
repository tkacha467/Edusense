"""Application exceptions."""
from typing import Any, Dict, Optional


class EduSenseException(Exception):
    """Base exception for EduSense AI."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize base exception."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail


class NotFoundException(EduSenseException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        detail: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize not found exception."""
        super().__init__(message=message, status_code=404, detail=detail)


class AlreadyExistsException(EduSenseException):
    """Exception raised when a resource already exists."""

    def __init__(
        self,
        message: str = "Resource already exists",
        detail: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize already exists exception."""
        super().__init__(message=message, status_code=409, detail=detail)


class ValidationException(EduSenseException):
    """Exception raised when validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        detail: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize validation exception."""
        super().__init__(message=message, status_code=422, detail=detail)


class UnauthorizedException(EduSenseException):
    """Exception raised when authentication fails."""

    def __init__(
        self,
        message: str = "Unauthorized access",
        detail: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize unauthorized exception."""
        super().__init__(message=message, status_code=401, detail=detail)


class ForbiddenException(EduSenseException):
    """Exception raised when authorization fails."""

    def __init__(
        self,
        message: str = "Forbidden access",
        detail: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize forbidden exception."""
        super().__init__(message=message, status_code=403, detail=detail)


class BadRequestException(EduSenseException):
    """Exception raised for bad requests."""

    def __init__(
        self,
        message: str = "Bad request",
        detail: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize bad request exception."""
        super().__init__(message=message, status_code=400, detail=detail)


class InternalServerException(EduSenseException):
    """Exception raised for internal server errors."""

    def __init__(
        self,
        message: str = "Internal server error",
        detail: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize internal server exception."""
        super().__init__(message=message, status_code=500, detail=detail)
