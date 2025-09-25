"""
Exception classes for Wakapi MCP server.

Extended version for unified error handling.
"""

from typing import Optional, Any
from enum import IntEnum


class ErrorCode(IntEnum):
    """Error code enumeration."""

    GENERIC = 1000
    CONFIGURATION = 1100
    AUTHENTICATION = 1200
    VALIDATION = 1300
    API = 1400
    NETWORK = 1500
    TOOL_EXECUTION = 1600
    NOT_FOUND = 1700
    PERMISSION = 1800


class WakapiError(Exception):
    """Base exception class for Wakapi-related errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.GENERIC,
        http_status: int = 500,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize the WakapiError."""
        self.message = message
        self.error_code = error_code
        self.http_status = http_status
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary format (for JSON response)."""
        return {
            "error": True,
            "message": self.message,
            "code": self.error_code.value,
            "http_status": self.http_status,
            "details": self.details,
        }


class ConfigurationError(WakapiError):
    """Configuration-related error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the ConfigurationError."""
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFIGURATION,
            http_status=400,
            details=details,
        )


class AuthenticationError(WakapiError):
    """Authentication-related error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the AuthenticationError."""
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION,
            http_status=401,
            details=details,
        )


class ApiError(WakapiError):
    """API call-related error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the ApiError."""
        super().__init__(
            message=message, error_code=ErrorCode.API, http_status=400, details=details
        )


class ValidationError(WakapiError):
    """Data validation-related error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the ValidationError."""
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION,
            http_status=400,
            details=details,
        )


class NetworkError(WakapiError):
    """Network-related error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize the NetworkError."""
        super().__init__(
            message=message,
            error_code=ErrorCode.NETWORK,
            http_status=503,
            details=details,
        )


class ToolExecutionError(WakapiError):
    """Tool execution-related error."""

    def __init__(
        self, message: str, tool_name: str, details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize the ToolExecutionError."""
        super_details = {"tool_name": tool_name, **(details or {})}
        super().__init__(
            message=message,
            error_code=ErrorCode.TOOL_EXECUTION,
            http_status=400,
            details=super_details,
        )


class NotFoundError(WakapiError):
    """Resource not found error."""

    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize the NotFoundError."""
        super_details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            **(details or {}),
        }
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            http_status=404,
            details=super_details,
        )


class PermissionError(WakapiError):
    """Permission-related error."""

    def __init__(
        self,
        message: str,
        required_permission: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize the PermissionError."""
        super_details = {"required_permission": required_permission, **(details or {})}
        super().__init__(
            message=message,
            error_code=ErrorCode.PERMISSION,
            http_status=403,
            details=super_details,
        )
