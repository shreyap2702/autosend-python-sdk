"""
Sending module for the Autosend SDK.
Provides methods for sending single and bulk emails via the Autosend API.
"""

from typing import Any, Dict
from autosend.client import AutosendClient


class Sending:
    """
    Resource class for managing email sending operations.

    Example:
        >>> from autosend.client import AutosendClient
        >>> client = AutosendClient(api_key="YOUR_API_KEY")
        >>> client.sending.send_email({
        ...     "to": {"email": "customer@example.com", "name": "Jane Smith"},
        ...     "from": {"email": "hello@mail.yourdomain.com", "name": "Your Company"},
        ...     "subject": "Welcome!",
        ...     "html": "<h1>Hello!</h1>",
        ...     "dynamicData": {"name": "Jane"}
        ... })
    """

    def __init__(self, client: AutosendClient) -> None:
        """
        Initialize the Sending resource with a shared AutosendClient instance.
        """
        self._client = client

    def send_email(self, data: Dict[str, Any]) -> Any:
        """
        Send a single email using the /mails/send endpoint.

        Args:
            data: A dictionary representing the email payload as per Autosend API.

        Required fields:
            - to: { "email": str, "name": str }
            - from: { "email": str, "name": str }
            - subject: str
            - html: str
            - dynamicData: dict
            - replyTo (optional): { "email": str }

        Returns:
            Parsed JSON response from the Autosend API.
        """
        return self._client.post("/mails/send", data=data)

    def send_bulk(self, data: Dict[str, Any]) -> Any:
        """
        Send multiple emails in bulk using the /mails/bulk endpoint.

        Args:
            data: A dictionary containing:
                - recipients: list of { "email": str, "name": str }
                - from: { "email": str, "name": str }
                - subject: str
                - html: str
                - dynamicData: dict
                - replyTo (optional): { "email": str }

        Returns:
            Parsed JSON response from the Autosend API.
        """
        return self._client.post("/mails/bulk", data=data)
