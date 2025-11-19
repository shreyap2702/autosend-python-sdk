"""
Sending module for the Autosend SDK.
Provides methods for sending single and bulk emails via the Autosend API.
"""

import re
import logging
from typing import Any, Dict, List, Optional
from autosend.client import AutosendClient
from autosend.errors import ValidationError


logger = logging.getLogger("autosend.sending")


class Sending:
    """
    Resource class for managing email sending operations.
    """

    def __init__(self, client: AutosendClient) -> None:
        """
        Initialize the Sending resource with a shared AutosendClient instance.
        """
        self._client = client

    @staticmethod
    def _extract_placeholders(html: str) -> set[str]:
        return set(re.findall(r"{{\s*(\w+)\s*}}", html))

    def _validate_dynamic_data(self, html: str, dynamic_data: Dict[str, Any]) -> None:
        placeholders = self._extract_placeholders(html)
        provided_keys = set(dynamic_data.keys())

        missing = placeholders - provided_keys
        extra = provided_keys - placeholders

        if missing:
            raise ValidationError(
                "Missing values for template placeholders",
                field="dynamicData",
                value=list(missing),
            )

        if placeholders and not dynamic_data:
            raise ValidationError(
                "HTML contains template placeholders but dynamicData is empty",
                field="dynamicData",
            )

        if extra:
            logger.debug(
                "dynamicData contains keys not used in the template: %s",
                list(extra),
            )

    def _validate_attachments(self, attachments: List[Dict[str, Any]] | None) -> None:
        if not attachments:
            return

        if len(attachments) > 20:
            raise ValidationError(
                "A maximum of 20 attachments is allowed.",
                field="attachments",
            )

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
            ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
            if ext in blocked_extensions:
                raise ValidationError(
                    f"Attachment type '{ext}' is not supported.",
                    field="attachments",
                    value=filename,
                )

    def _validate_unsubscribe(self, unsubscribe_url: str | None) -> None:
        """Validate unsubscribe URL format."""
        if unsubscribe_url:
            if not unsubscribe_url.startswith(("http://", "https://")):
                raise ValidationError(
                    "Unsubscribe URL must start with http:// or https://",
                    field="unsubscribeUrl",
                    value=unsubscribe_url,
                )

    #1. SEND SINGLE EMAIL
    def send_email(
    self,
    to_email: str,
    to_name: str,
    from_email: str,
    from_name: str,
    subject: str,
    html: str,
    dynamic_data: Dict[str, Any],
    reply_to_email: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    unsubscribe_url: Optional[str] = None,
    unsubscribe_group_id: Optional[str] = None,
    ) -> Any:
        """
        Send a transactional or marketing email via the AutoSend API.
        
        This method sends a single email using the /mails/send endpoint. Either a
        templateId OR html/text content must be provided. When using a template,
        the subject is optional.
        
        Args:
            to_email (str): Recipient's email address.
            to_name (str): Recipient's display name.
            from_email (str): Sender's email address.
            from_name (str): Sender's display name.
            subject (str): Email subject line.
            html (str): HTML content of the email body.
            dynamic_data (Dict[str, Any]): Dictionary containing dynamic variables
                to be injected into the email template or content.
            reply_to_email (Optional[str], optional): Email address for replies.
                Defaults to None.
            attachments (Optional[List[Dict[str, Any]]], optional): List of attachment
                objects. Each attachment should contain required fields as per API spec.
                Defaults to None.
            unsubscribe_url (Optional[str], optional): RFC 2369 compliant URL for the
                unsubscribe link. Defaults to None.
            unsubscribe_group_id (Optional[str], optional): Subscription group or
                category ID for managing unsubscribe preferences. Defaults to None.
        
        Returns:
            Any: API response from the /mails/send endpoint.
        
        Raises:
            ValidationError: If attachments, dynamic_data, or unsubscribe_url fail
                validation checks.
            APIError: If the API request fails.
        
        Example:
            >>> client.send_email(
            ...     to_email="user@example.com",
            ...     to_name="John Doe",
            ...     from_email="noreply@company.com",
            ...     from_name="Company Name",
            ...     subject="Welcome to our service",
            ...     html="<h1>Welcome {{name}}!</h1>",
            ...     dynamic_data={"name": "John"},
            ...     reply_to_email="support@company.com",
            ...     unsubscribe_url="https://company.com/unsubscribe"
            ... )
        
        API Endpoint:
            POST https://api.autosend.com/v1/mails/send
        """
        logger.info("Preparing to send a single email to %s", to_email)

        # Validate attachments
        self._validate_attachments(attachments)

        # Validate dynamicData against template
        self._validate_dynamic_data(html, dynamic_data)

        # Validate unsubscribe URL
        self._validate_unsubscribe(unsubscribe_url)

        # Build payload
        payload: Dict[str, Any] = {
            "to": {"email": to_email, "name": to_name},
            "from": {"email": from_email, "name": from_name},
            "subject": subject,
            "html": html,
            "dynamicData": dynamic_data,
        }

        # Add optional reply-to address
        if reply_to_email:
            payload["replyTo"] = {"email": reply_to_email}

        # Add attachments if provided
        if attachments:
            payload["attachments"] = attachments

        # Add unsubscribe functionality
        if unsubscribe_url or unsubscribe_group_id:
            unsubscribe_data: Dict[str, Any] = {}
            if unsubscribe_url:
                unsubscribe_data["url"] = unsubscribe_url
            if unsubscribe_group_id:
                unsubscribe_data["groupId"] = unsubscribe_group_id
            payload["unsubscribe"] = unsubscribe_data
            logger.debug("Unsubscribe configuration added to email payload.")

        logger.debug("Single email payload validated and ready for sending.")

        # Send request to API
        return self._client.post("/mails/send", data=payload)

    #2. SEND BULK EMAIL
    def send_bulk(
    self,
    recipients: List[Dict[str, str]],
    from_email: str,
    from_name: str,
    subject: str,
    html: str,
    dynamic_data: Dict[str, Any],
    reply_to_email: Optional[str] = None,
    unsubscribe_url: Optional[str] = None,
    unsubscribe_group_id: Optional[str] = None,
    ) -> Any:
        """
        Send the same email to multiple recipients in a single API request.
        
        This method sends bulk emails using the /mails/bulk endpoint. All recipients
        receive the same email content with support for dynamic data personalization.
        
        Args:
            recipients (List[Dict[str, str]]): List of recipient dictionaries. Each must
                contain 'email' and 'name' keys. Maximum 100 recipients per request.
                Example: [{"email": "user@example.com", "name": "John Doe"}]
            from_email (str): Sender's email address.
            from_name (str): Sender's display name.
            subject (str): Email subject line.
            html (str): Email body in HTML format. Can include dynamic data placeholders.
            dynamic_data (Dict[str, Any]): Dictionary of dynamic data for template
                personalization. Keys should match placeholders in the HTML content.
            reply_to_email (Optional[str], optional): Email address for replies. 
                Defaults to None.
            unsubscribe_url (Optional[str], optional): URL for the unsubscribe link
                (RFC 2369 compliant). Defaults to None.
            unsubscribe_group_id (Optional[str], optional): Subscription group/category
                ID for managing unsubscribe preferences. Defaults to None.
        
        Returns:
            Any: API response from the bulk email send operation.
        
        Raises:
            ValidationError: If recipients list is empty, exceeds 100 recipients,
                contains invalid recipient data, has invalid dynamic data template usage,
                or has an invalid unsubscribe URL.
        
        Example:
            >>> recipients = [
            ...     {"email": "user1@example.com", "name": "Alice"},
            ...     {"email": "user2@example.com", "name": "Bob"}
            ... ]
            >>> response = client.send_bulk(
            ...     recipients=recipients,
            ...     from_email="sender@example.com",
            ...     from_name="Company Name",
            ...     subject="Newsletter",
            ...     html="<p>Hello {{name}}</p>",
            ...     dynamic_data={"name": "placeholder"},
            ...     unsubscribe_url="https://example.com/unsubscribe"
            ... )
        """
        logger.info("Preparing bulk email send for %d recipients", len(recipients))

        # Validate recipients list is not empty
        if not recipients:
            raise ValidationError(
                "The recipients list must contain at least one recipient.",
                field="recipients",
            )

        # Validate recipients count does not exceed maximum
        if len(recipients) > 100:
            raise ValidationError(
                "A maximum of 100 recipients is allowed for bulk email.",
                field="recipients",
            )

        # Validate each recipient has required fields
        for recipient in recipients:
            if "email" not in recipient or "name" not in recipient:
                raise ValidationError(
                    "Each recipient must include 'email' and 'name'.",
                    field="recipients",
                    value=recipient,
                )

        # Validate dynamic data template usage
        self._validate_dynamic_data(html, dynamic_data)

        # Validate unsubscribe URL format
        self._validate_unsubscribe(unsubscribe_url)

        # Build request payload
        payload: Dict[str, Any] = {
            "recipients": recipients,
            "from": {"email": from_email, "name": from_name},
            "subject": subject,
            "html": html,
            "dynamicData": dynamic_data,
        }

        # Add optional reply-to address
        if reply_to_email:
            payload["replyTo"] = {"email": reply_to_email}

        # Add optional unsubscribe functionality
        if unsubscribe_url or unsubscribe_group_id:
            unsubscribe_data: Dict[str, Any] = {}
            if unsubscribe_url:
                unsubscribe_data["url"] = unsubscribe_url
            if unsubscribe_group_id:
                unsubscribe_data["groupId"] = unsubscribe_group_id
            payload["unsubscribe"] = unsubscribe_data
            logger.debug("Unsubscribe configuration added to bulk email payload.")

        logger.debug("Bulk email payload validated and ready for sending.")

        # Send bulk email request
        return self._client.post("/mails/bulk", data=payload)