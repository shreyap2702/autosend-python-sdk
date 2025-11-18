"""
Custom exceptions for the Autosend SDK.
All exceptions in this module inherit from AutosendError.
"""


class AutosendError(Exception):
    """
    Base class for all exceptions raised by the Autosend SDK.
    All custom exceptions should inherit from this class.
    """
    pass


class AuthenticationError(AutosendError):
    """
    Raised when the provided API key is invalid or missing.
    Typically corresponds to HTTP 401 Unauthorized.
    """
    pass


class RequestError(AutosendError):
    """
    Raised when an HTTP request fails due to client or network issues.
    For example: connection errors, timeouts, or malformed requests.
    """
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(AutosendError):
    """
    Raised when invalid arguments or payload data are passed to SDK methods.

    Attributes:
        field (str): The specific field that failed validation (optional).
        value (Any): The invalid value provided (optional).
    """

    def __init__(self, message: str, field: str | None = None, value: object | None = None):
        self.field = field
        self.value = value

        error_msg = message
        if field is not None:
            error_msg += f" (field='{field}')"
        if value is not None:
            error_msg += f" (value='{value}')"

        super().__init__(error_msg)
