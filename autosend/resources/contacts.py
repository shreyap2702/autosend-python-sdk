"""
Contacts module for the Autosend SDK.
Provides methods for creating, updating, removing, searching, and retrieving contacts.
"""

from typing import Any, Dict, List
from autosend.client import AutosendClient


class Contacts:
    """
    Resource class for managing contact operations through the Autosend SDK.

    Example:
        >>> from autosend.client import AutosendClient
        >>> client = AutosendClient(api_key="YOUR_API_KEY")
        >>> client.contacts.create_contact({
        ...     "email": "john.doe@example.com",
        ...     "firstName": "John",
        ...     "lastName": "Doe",
        ...     "userId": "user_12345",
        ...     "customFields": {
        ...         "company": "Acme Corp",
        ...         "role": "Developer",
        ...         "plan": "premium"
        ...     }
        ... })
    """

    def __init__(self, client: AutosendClient) -> None:
        """
        Initialize the Contacts resource with a shared AutosendClient instance.
        """
        self._client = client

    # 1. Create Contact
    def create_contact(
        self,
        email: str,
        first_name: str,
        last_name: str,
        user_id: str | None = None,
        custom_fields: Dict[str, Any] | None = None,
    ) -> Any:
        """
        Create a new contact using /contacts.

        Args:
            email: The contact's email address.
            first_name: First name of the contact.
            last_name: Last name of the contact.
            user_id: Optional user identifier for the contact.
            custom_fields: Optional dictionary of additional fields defined in Autosend.

        Returns:
            JSON response from the API.
        """
        payload = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
        }

        if user_id is not None:
            payload["userId"] = user_id

        if custom_fields is not None:
            payload["customFields"] = custom_fields

        return self._client.post("/contacts", data=payload)

    # 2. Upsert Contact (create or update by email)
    def upsert_contact(
        self,
        email: str,
        first_name: str,
        last_name: str,
        user_id: str | None = None,
        custom_fields: Dict[str, Any] | None = None,
    ) -> Any:
        """
        Create or update a contact using the /contacts/email endpoint (upsert).

        Args:
            email: The contact's email address.
            first_name: First name of the contact.
            last_name: Last name of the contact.
            user_id: Optional user identifier for the contact.
            custom_fields: Optional dictionary of additional fields for the contact.

        Returns:
            JSON response from the Autosend API.
        """
        payload: Dict[str, Any] = {
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
        }

        if user_id is not None:
            payload["userId"] = user_id

        if custom_fields is not None:
            payload["customFields"] = custom_fields

        return self._client.post("/contacts/email", data=payload)


    # 3. Remove Contacts (delete multiple by email)
    def remove_contacts(self, emails: List[str]) -> Any:
        """
        Remove one or more contacts using /contacts/remove.

        Args:
            emails: A list of email addresses to remove.
                    Must contain at least one email.

        Raises:
            ValueError: If the emails list is empty.

        Returns:
            JSON response from the Autosend API.
        """
        if not emails:
            raise ValueError("At least one email is required to remove contacts.")

        payload = emails

        return self._client.post("/contacts/remove", data=payload)
    
    # 4. Get a Contact by ID
    def get_contact(self, contact_id: str) -> Any:
        """
        Retrieve a contact by its ID using /contacts/{id}.

        Args:
            contact_id: Unique contact ID.

        Raises:
            ValueError: If contact_id is empty.

        Returns:
            JSON response from the Autosend API.
        """
        if not contact_id:
            raise ValueError("contact_id is required to fetch a contact.")

        return self._client.get(f"/contacts/{contact_id}")

    # 5. Search Contacts by Email
    def search_by_emails(self, emails: List[str]) -> Any:
        """
        Search for multiple contacts by their email addresses using
        /contacts/search/emails.

        Args:
            emails: List of email addresses to search. Must contain at least 1 email.

        Raises:
            ValueError: If the list is empty.

        Returns:
            JSON response from the Autosend API containing matching contacts.
        """
        if not emails:
            raise ValueError("At least one email is required for searching contacts.")

        payload = emails

        return self._client.post("/contacts/search/emails", data=payload)

    # 6. Bulk Update Contacts
    def bulk_update(
        self, contacts: List[Dict[str, Any]], run_workflow: bool = False
    ) -> Any:
        """
        Bulk update multiple contacts using /contacts/bulk-update.

        Args:
            contacts: List of contact objects.
            run_workflow: Whether to run workflows (default: False).

        Returns:
            JSON response from the API.
        """
        payload = {
            "contacts": contacts,
            "runWorkflow": run_workflow,
        }
        return self._client.post("/contacts/bulk-update", data=payload)

    # 7. Delete Contact by User ID
    def delete_by_user_id(self, user_id: str) -> Any:
        """
        Delete a contact by its userId using /contacts/email/userId/{userId}.

        Args:
            user_id: The user identifier used in your application.

        Raises:
            ValueError: If user_id is empty.

        Returns:
            JSON response from the Autosend API.
        """
        if not user_id:
            raise ValueError("user_id is required to delete a contact.")

        return self._client.delete(f"/contacts/email/userId/{user_id}")


    # 8. Delete Contact by ID (same endpoint as above? API inconsistency)
    def delete_by_id(self, contact_id: str) -> Any:
        """
        Delete a contact using /contacts/{id}.

        Args:
            contact_id: The unique ID of the contact.

        Raises:
            ValueError: If contact_id is empty.

        Returns:
            JSON response from the Autosend API.
        """
        if not contact_id:
            raise ValueError("contact_id is required to delete a contact.")

        return self._client.delete(f"/contacts/{contact_id}")


    # 9. Get Unsubscribe Groups for Contact
    def get_unsubscribe_groups(self, contact_id: str) -> Any:
        """
        Get unsubscribe groups for a contact using /contacts/{id}/unsubscribe-groups.

        Args:
            contact_id: Unique ID of the contact.

        Returns:
            JSON response from the API.
        """
        return self._client.get(f"/contacts/{contact_id}/unsubscribe-groups")
