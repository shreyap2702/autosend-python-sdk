"""
Contacts module for the Autosend SDK.
Provides methods for creating, updating, removing, searching, and retrieving contacts.
"""

import logging
from typing import Any, Dict, List
from autosend.client import AutosendClient
from autosend.errors import ValidationError


logger = logging.getLogger("autosend.contacts")


class Contacts:
    """
    Resource class for managing contact operations through the Autosend SDK.
    """

    def __init__(self, client: AutosendClient) -> None:
        self._client = client

    # ---------------------------------------------------------
    # Utility: Validate email format
    # ---------------------------------------------------------
    @staticmethod
    def _validate_email(email: str, field: str = "email") -> None:
        if not email or "@" not in email:
            raise ValidationError("Invalid email address.", field=field, value=email)

    # ---------------------------------------------------------
    # Utility: Validate string fields
    # ---------------------------------------------------------
    @staticmethod
    def _validate_non_empty(value: str, field: str) -> None:
        if not value or not value.strip():
            raise ValidationError(f"{field} cannot be empty.", field=field, value=value)

    # ---------------------------------------------------------
    # 1. Create Contact
    # ---------------------------------------------------------
    def create_contact(
        self,
        email: str,
        first_name: str,
        last_name: str,
        user_id: str | None = None,
        custom_fields: Dict[str, Any] | None = None,
    ) -> Any:

        logger.info("Creating contact: %s", email)

        # Validate required fields
        self._validate_email(email)
        self._validate_non_empty(first_name, "firstName")
        self._validate_non_empty(last_name, "lastName")

        # Validate optional fields
        if custom_fields is not None and not isinstance(custom_fields, dict):
            raise ValidationError(
                "custom_fields must be a dictionary.", field="customFields"
            )

        payload = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
        }

        if user_id:
            payload["userId"] = user_id

        if custom_fields:
            payload["customFields"] = custom_fields

        logger.debug("Contact payload validated and ready for creation.")
        return self._client.post("/contacts", data=payload)

    # ---------------------------------------------------------
    # 2. Upsert Contact
    # ---------------------------------------------------------
    def upsert_contact(
        self,
        email: str,
        first_name: str,
        last_name: str,
        user_id: str | None = None,
        custom_fields: Dict[str, Any] | None = None,
    ) -> Any:

        logger.info("Upserting contact: %s", email)

        self._validate_email(email)
        self._validate_non_empty(first_name, "firstName")
        self._validate_non_empty(last_name, "lastName")

        if custom_fields is not None and not isinstance(custom_fields, dict):
            raise ValidationError("custom_fields must be a dictionary.", field="customFields")

        payload = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
        }

        if user_id:
            payload["userId"] = user_id

        if custom_fields:
            payload["customFields"] = custom_fields

        logger.debug("Contact payload validated for upsert.")
        return self._client.post("/contacts/email", data=payload)

    # ---------------------------------------------------------
    # 3. Remove Contacts
    # ---------------------------------------------------------
    def remove_contacts(self, emails: List[str]) -> Any:

        logger.info("Removing %d contacts", len(emails))

        if not emails:
            raise ValidationError("At least one email is required.", field="emails")

        for email in emails:
            self._validate_email(email)

        logger.debug("Email list validated for removal.")
        return self._client.post("/contacts/remove", data=emails)

    # ---------------------------------------------------------
    # 4. Get Contact by ID
    # ---------------------------------------------------------
    def get_contact(self, contact_id: str) -> Any:

        logger.info("Fetching contact: %s", contact_id)

        self._validate_non_empty(contact_id, "contact_id")

        return self._client.get(f"/contacts/{contact_id}")

    # ---------------------------------------------------------
    # 5. Search Contacts by Email
    # ---------------------------------------------------------
    def search_by_emails(self, emails: List[str]) -> Any:

        logger.info("Searching contacts by %d emails", len(emails))

        if not emails:
            raise ValidationError("At least one email is required.", field="emails")

        for email in emails:
            self._validate_email(email)

        logger.debug("Email list validated for search.")
        return self._client.post("/contacts/search/emails", data=emails)

    # ---------------------------------------------------------
    # 6. Bulk Update Contacts
    # ---------------------------------------------------------
    def bulk_update(
        self,
        contacts: List[Dict[str, Any]],
        run_workflow: bool = False
    ) -> Any:

        logger.info("Bulk updating %d contacts", len(contacts))

        if not contacts:
            raise ValidationError("Contacts list cannot be empty.", field="contacts")

        if not isinstance(contacts, list):
            raise ValidationError("Contacts must be a list.", field="contacts")

        for contact in contacts:
            if "email" not in contact:
                raise ValidationError(
                    "Each contact must contain an email field.",
                    field="contacts",
                    value=contact,
                )
            self._validate_email(contact["email"])

        payload = {"contacts": contacts, "runWorkflow": run_workflow}

        logger.debug("Bulk update payload validated.")
        return self._client.post("/contacts/bulk-update", data=payload)

    # ---------------------------------------------------------
    # 7. Delete Contact by User ID
    # ---------------------------------------------------------
    def delete_by_user_id(self, user_id: str) -> Any:

        logger.info("Deleting contact by user_id: %s", user_id)

        self._validate_non_empty(user_id, "user_id")

        return self._client.delete(f"/contacts/email/userId/{user_id}")

    # ---------------------------------------------------------
    # 8. Delete Contact by ID
    # ---------------------------------------------------------
    def delete_by_id(self, contact_id: str) -> Any:

        logger.info("Deleting contact by ID: %s", contact_id)

        self._validate_non_empty(contact_id, "contact_id")

        return self._client.delete(f"/contacts/{contact_id}")

    # ---------------------------------------------------------
    # 9. Get Unsubscribe Groups
    # ---------------------------------------------------------
    def get_unsubscribe_groups(self, contact_id: str) -> Any:

        logger.info("Fetching unsubscribe groups for: %s", contact_id)

        self._validate_non_empty(contact_id, "contact_id")

        return self._client.get(f"/contacts/{contact_id}/unsubscribe-groups")
