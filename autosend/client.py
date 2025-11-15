"""
Client module for interacting with the Autosend API.
Handles authentication, HTTP requests, resource access, and error management.
"""

from typing import Any, Dict
import requests

from autosend.errors import AutosendError, AuthenticationError, RequestError


class AutosendClient:
    """
    Core client for interacting with the Autosend API.

    Example:
        >>> from autosend import client
        >>> autosend = client.AutosendClient(api_key="YOUR_API_KEY")
        >>> autosend.sending.send_email({...})
    """

    def __init__(self, api_key: str, base_url: str = "https://api.autosend.com/v1") -> None:
        """
        Initialize the Autosend API client.

        Args:
            api_key: Your Autosend API key.
            base_url: Base URL of the Autosend API (default: production endpoint).

        Raises:
            AuthenticationError: If API key is empty or invalid.
        """
        if not api_key or not api_key.strip():
            raise AuthenticationError("API key cannot be empty.")
        
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self._attach_resources()


    def _attach_resources(self) -> None:
        """
        Dynamically import and attach resource modules.
        Keeps imports local to avoid circular dependencies.
        """
        from autosend.resources.sending import Sending
        from autosend.resources.contacts import Contacts

        self.sending = Sending(self)
        self.contacts = Contacts(self)

    def _headers(self) -> Dict[str, str]:
        """
        Build default headers for all API requests.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """
        Internal helper for making HTTP requests.

        Args:
            method: HTTP method ('GET', 'POST', 'DELETE', etc.)
            endpoint: API path, e.g. '/mails/send'
            **kwargs: Extra arguments passed to requests.request()

        Returns:
            Parsed JSON response or raw text if not JSON.

        Raises:
            AuthenticationError: For invalid/missing API key.
            RequestError: For network issues (timeouts, etc.).
            AutosendError: For API-level errors (non-200 responses).
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._headers()

        try:
            response = requests.request(method, url, headers=headers, timeout=15, **kwargs)
        except requests.RequestException as exc:
            raise RequestError(f"HTTP request failed: {exc}") from exc
        if response.status_code == 401:
            raise AuthenticationError("Invalid or unauthorized API key.")
        if not response.ok:
            raise AutosendError(f"API returned {response.status_code}: {response.text}")

        try:
            return response.json()
        except ValueError:
            return response.text
        
    # Public HTTP Methods

    def get(self, endpoint: str, **kwargs: Any) -> Any:
        """Send a GET request to the Autosend API."""
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, data: Dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """Send a POST request to the Autosend API."""
        return self._request("POST", endpoint, json=data, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Any:
        """Send a DELETE request to the Autosend API."""
        return self._request("DELETE", endpoint, **kwargs)
