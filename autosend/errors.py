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
