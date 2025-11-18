"""
Sending module for the Autosend SDK.
Provides methods for sending single and bulk emails via the Autosend API.
"""

import re
import logging
from typing import Any, Dict, List
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
        reply_to_email: str | None = None,
        attachments: List[Dict[str, Any]] | None = None,
        unsubscribe_url: str | None = None,
        unsubscribe_group_id: str | None = None,
    ) -> Any:
        """
        Send a single email using the /mails/send endpoint.
        
        Args:
            unsubscribe_url: URL for the unsubscribe link (RFC 2369 compliant)
            unsubscribe_group_id: Optional subscription group/category ID
        """

        logger.info("Preparing to send a single email to %s", to_email)

        # Validate attachments
        self._validate_attachments(attachments)

        # Validate dynamicData against template
        self._validate_dynamic_data(html, dynamic_data)

        # Validate unsubscribe URL
        self._validate_unsubscribe(unsubscribe_url)

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

        # Send request
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
        reply_to_email: str | None = None,
        unsubscribe_url: str | None = None,
        unsubscribe_group_id: str | None = None,
    ) -> Any:
        """
        Send multiple emails using the /mails/bulk endpoint.
        
        Args:
            unsubscribe_url: URL for the unsubscribe link (RFC 2369 compliant)
            unsubscribe_group_id: Optional subscription group/category ID
        """

        logger.info("Preparing bulk email send for %d recipients", len(recipients))

        if not recipients:
            raise ValidationError(
                "The recipients list must contain at least one recipient.",
                field="recipients",
            )

        if len(recipients) > 100:
            raise ValidationError(
                "A maximum of 100 recipients is allowed for bulk email.",
                field="recipients",
            )

        for recipient in recipients:
            if "email" not in recipient or "name" not in recipient:
                raise ValidationError(
                    "Each recipient must include 'email' and 'name'.",
                    field="recipients",
                    value=recipient,
                )

        # Validate dynamic data template usage
        self._validate_dynamic_data(html, dynamic_data)

        # Validate unsubscribe URL
        self._validate_unsubscribe(unsubscribe_url)

        payload: Dict[str, Any] = {
            "recipients": recipients,
            "from": {"email": from_email, "name": from_name},
            "subject": subject,
            "html": html,
            "dynamicData": dynamic_data,
        }

        if reply_to_email:
            payload["replyTo"] = {"email": reply_to_email}

        # Add unsubscribe functionality
        if unsubscribe_url or unsubscribe_group_id:
            unsubscribe_data: Dict[str, Any] = {}
            if unsubscribe_url:
                unsubscribe_data["url"] = unsubscribe_url
            if unsubscribe_group_id:
                unsubscribe_data["groupId"] = unsubscribe_group_id
            payload["unsubscribe"] = unsubscribe_data
            logger.debug("Unsubscribe configuration added to bulk email payload.")

        logger.debug("Bulk email payload validated and ready for sending.")

        return self._client.post("/mails/bulk", data=payload)