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

    def send_email(
    self,
    to_email: str,
    to_name: str,
    from_email: str,
    from_name: str,
    subject: str,
    html: str,
    dynamic_data: Dict[str, Any],
    reply_to_email: str | None = None,
    attachments: List[Dict[str, Any]] | None = None,
    ) -> Any:
        """
        Send a single email using the /mails/send endpoint.

        Args:
            to_email: Recipient email address.
            to_name: Recipient name.
            from_email: Sender email address.
            from_name: Sender name.
            subject: Email subject text.
            html: HTML body of the email.
            dynamic_data: Template variables for the email.
            reply_to_email: Optional reply-to email.
            attachments: Optional list of attachments. Maximum 20 allowed.

        Raises:
            ValueError: If attachments exceed allowed count or have blocked file types.

        Returns:
            Parsed JSON response from the Autosend API.
        """

        # Attachment validations
        if attachments:
            if len(attachments) > 20:
                raise ValueError("A maximum of 20 attachments is allowed.")

            blocked_extensions = {
                ".adp", ".app", ".asp", ".bas", ".bat", ".cer", ".chm", ".cmd", ".com",
                ".cpl", ".crt", ".csh", ".der", ".exe", ".fxp", ".gadget", ".hlp", ".hta",
                ".inf", ".ins", ".isp", ".its", ".js", ".jse", ".ksh", ".lib", ".lnk",
                ".mad", ".maf", ".mag", ".mam", ".maq", ".mar", ".mas", ".mat", ".mau",
                ".mav", ".maw", ".mda", ".mdb", ".mde", ".mdt", ".mdw", ".mdz", ".msc",
                ".msh", ".msh1", ".msh2", ".mshxml", ".msh1xml", ".msh2xml", ".msi",
                ".msp", ".mst", ".ops", ".pcd", ".pif", ".plg", ".prf", ".prg", ".reg",
                ".scf", ".scr", ".sct", ".shb", ".shs", ".sys", ".ps1", ".ps1xml", ".ps2",
                ".ps2xml", ".psc1", ".psc2", ".tmp", ".url", ".vb", ".vbe", ".vbs", ".vps",
                ".vsmacros", ".vss", ".vst", ".vsw", ".vxd", ".ws", ".wsc", ".wsf", ".wsh",
                ".xnk"
            }

            for file in attachments:
                filename = file.get("filename", "")
                ext = f".{filename.split('.')[-1].lower()}" if "." in filename else ""
                if ext in blocked_extensions:
                    raise ValueError(f"Attachment type '{ext}' is not supported.")

        # Build payload
        payload = {
            "to": {"email": to_email, "name": to_name},
            "from": {"email": from_email, "name": from_name},
            "subject": subject,
            "html": html,
            "dynamicData": dynamic_data,
        }

        if reply_to_email:
            payload["replyTo"] = {"email": reply_to_email}

        if attachments:
            payload["attachments"] = attachments

        # Execute request
        return self._client.post("/mails/send", data=payload)


    def send_bulk(
        self,
        recipients: List[Dict[str, str]],
        from_email: str,
        from_name: str,
        subject: str,
        html: str,
        dynamic_data: Dict[str, Any],
        reply_to_email: str | None = None,
        attachments: List[Dict[str, Any]] | None = None,
    ) -> Any:
        """
        Send multiple emails in bulk using the /mails/bulk endpoint.

        Args:
            recipients: A list of recipients where each item contains:
                {
                    "email": str,
                    "name": str
                }
                Maximum of 100 recipients allowed per request.

            from_email: Sender email address.
            from_name: Sender name.
            subject: The subject of the email.
            html: HTML body of the email.
            dynamic_data: Template variables for personalizing content.
            reply_to_email: Optional reply-to email address.
            attachments: Optional list of attachments (max 20 files).

        Raises:
            ValueError: If recipient or attachment rules are violated.

        Returns:
            JSON response from the Autosend API.
        """

    def send_bulk(
        self,
        recipients: List[Dict[str, str]],
        from_email: str,
        from_name: str,
        subject: str,
        html: str,
        dynamic_data: Dict[str, Any],
        reply_to_email: str | None = None,
    ) -> Any:
        """
        Send multiple emails in bulk using the /mails/bulk endpoint.

        Args:
            recipients: List of recipient objects, each with 'email' and 'name'.
                        Maximum of 100 recipients.
            from_email: Sender email address.
            from_name: Sender name.
            subject: Email subject.
            html: Email HTML body.
            dynamic_data: Template variables for email.
            reply_to_email: Optional reply-to email.

        Raises:
            ValueError: If recipients list is empty or exceeds 100, or if required keys missing.

        Returns:
            JSON response from the Autosend API.
        """
        if not recipients:
            raise ValueError("The recipients list must contain at least one recipient.")
        if len(recipients) > 100:
            raise ValueError("Maximum of 100 recipients allowed for bulk email.")

        for recipient in recipients:
            if "email" not in recipient or "name" not in recipient:
                raise ValueError("Each recipient must include 'email' and 'name'.")

        payload: Dict[str, Any] = {
            "recipients": recipients,
            "from": {"email": from_email, "name": from_name},
            "subject": subject,
            "html": html,
            "dynamicData": dynamic_data,
        }

        if reply_to_email:
            payload["replyTo"] = {"email": reply_to_email}

        return self._client.post("/mails/bulk", data=payload)
