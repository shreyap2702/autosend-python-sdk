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
        """
        Create a new contact in the system.

        Args:
            email (str): The contact's email address. Must be a valid email format.
            first_name (str): The contact's first name. Cannot be empty.
            last_name (str): The contact's last name. Cannot be empty.
            user_id (str | None, optional): Optional user ID to associate with the contact.
                Defaults to None.
            custom_fields (Dict[str, Any] | None, optional): Optional dictionary of custom
                field key-value pairs to attach to the contact. Defaults to None.

        Returns:
            Any: The API response containing the created contact data.

        Raises:
            ValidationError: If email format is invalid, if first_name or last_name are empty,
                or if custom_fields is not a dictionary.

        Example:
            >>> contact = client.create_contact(
            ...     email="john.doe@example.com",
            ...     first_name="John",
            ...     last_name="Doe",
            ...     user_id="user_123",
            ...     custom_fields={"company": "Acme Corp", "role": "Developer"}
            ... )
        """
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

        # Build request payload
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
        """
        Create a new contact or update an existing contact if the email already exists.
        
        This is the recommended endpoint for most contact synchronization scenarios.
        
        Args:
            email (str): The contact's email address. Must be a valid email format.
            first_name (str): The contact's first name. Cannot be empty.
            last_name (str): The contact's last name. Cannot be empty.
            user_id (str | None, optional): An optional user identifier to associate 
                with the contact. Defaults to None.
            custom_fields (Dict[str, Any] | None, optional): A dictionary of custom 
                field key-value pairs to store additional contact information. 
                Defaults to None.
        
        Returns:
            Any: The API response containing the created or updated contact data.
        
        Raises:
            ValidationError: If email format is invalid, first_name or last_name is 
                empty, or custom_fields is not a dictionary.
        
        Example:
            >>> client.upsert_contact(
            ...     email="john.doe@example.com",
            ...     first_name="John",
            ...     last_name="Doe",
            ...     user_id="user_123",
            ...     custom_fields={"company": "Acme Corp", "role": "Developer"}
            ... )
        
        API Endpoint:
            POST https://api.autosend.com/v1/contacts/email
        """
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
        """
        Remove one or more contacts by their email addresses.
        
        This method validates the provided email addresses and sends a request
        to remove the corresponding contacts from the system.
        
        Args:
            emails (List[str]): A list of email addresses of contacts to be removed.
                            Must contain at least one email address.
        
        Returns:
            Any: The IDs of the contacts that were successfully removed.
        
        Raises:
            ValidationError: If the emails list is empty or if any email address
                            is invalid.
        
        Example:
            >>> client.remove_contacts(['user@example.com', 'contact@test.com'])
            {'removed_ids': [123, 456]}
        
        API Endpoint:
            POST https://api.autosend.com/v1/contacts/remove
        """
        logger.info("Removing %d contacts", len(emails))
        
        # Validate that at least one email is provided
        if not emails:
            raise ValidationError("At least one email is required.", field="emails")
        
        # Validate each email address
        for email in emails:
            self._validate_email(email)
        
        logger.debug("Email list validated for removal.")
        
        # Send request to remove contacts
        return self._client.post("/contacts/remove", data=emails)

    # ---------------------------------------------------------
    # 4. Get Contact by ID
    # ---------------------------------------------------------
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Retrieve a single contact by its unique identifier.
        
        Fetches contact details from the AutoSend API using the provided
        contact ID. This method makes a GET request to the /contacts/{id}
        endpoint.
        
        Args:
            contact_id (str): The unique identifier of the contact to retrieve.
                Must be a non-empty string.
        
        Returns:
            Dict[str, Any]: A dictionary containing the contact information,
                including fields such as name, email, phone, and other
                contact details as defined by the API.
        
        Raises:
            ValueError: If contact_id is empty or None.
            APIError: If the API request fails or returns an error status.
            NotFoundError: If the contact with the given ID does not exist.
        
        Example:
            >>> client = AutoSendClient(api_key="your_api_key")
            >>> contact = client.get_contact("contact_123")
            >>> print(contact["email"])
            'user@example.com'
        
        API Endpoint:
            GET https://api.autosend.com/v1/contacts/{id}
        
        Note:
            This method requires valid authentication credentials to be
            configured in the client instance.
        """
        logger.info("Fetching contact with ID: %s", contact_id)
        
        # Validate input parameters
        self._validate_non_empty(contact_id, "contact_id")
        
        # Make API request
        endpoint = f"/contacts/{contact_id}"
        response = self._client.get(endpoint)
        
        logger.debug("Successfully retrieved contact: %s", contact_id)
        
        return response

    # ---------------------------------------------------------
    # 5. Search Contacts by Email
    # ---------------------------------------------------------

    def search_by_emails(self, emails: List[str]) -> Dict[str, Any]:
        """
        Search for contacts by their email addresses.
        
        Searches the AutoSend API for contacts matching the provided email
        addresses. This method makes a POST request to the /contacts/search/emails
        endpoint with a list of email addresses.
        
        Args:
            emails (List[str]): A list of email addresses to search for.
                Must contain at least one valid email address. Each email
                must be properly formatted.
        
        Returns:
            Dict[str, Any]: A dictionary containing the search results,
                including matched contacts and their details.
        
        Raises:
            ValidationError: If the emails list is empty or if any email
                address is invalid or improperly formatted.
            APIError: If the API request fails or returns an error status.
        
        Example:
            >>> client = AutoSendClient(api_key="your_api_key")
            >>> results = client.search_by_emails(["user1@example.com", "user2@example.com"])
            >>> print(len(results["contacts"]))
            2
        
        API Endpoint:
            POST https://api.autosend.com/v1/contacts/search/emails
        
        Note:
            This method requires valid authentication credentials to be
            configured in the client instance. All email addresses are
            validated before making the API request.
        """
        logger.info("Searching contacts by %d emails", len(emails))
        
        # Validate input parameters
        if not emails:
            raise ValidationError("At least one email is required.", field="emails")
        
        for email in emails:
            self._validate_email(email)
        
        logger.debug("Email list validated for search.")
        
        # Make API request
        response = self._client.post("/contacts/search/emails", data=emails)
        
        return response

    # ---------------------------------------------------------
    # 6. Bulk Update Contacts
    # ---------------------------------------------------------
    def bulk_update(
        self,
        contacts: List[Dict[str, Any]],
        run_workflow: bool = False
    ) -> Dict[str, Any]:
        """
        Updates or creates multiple contacts in a single API request.
        
        Each contact is either created (if it doesn't exist) or updated (if it does)
        based on the email address. This method allows you to efficiently manage
        multiple contacts in a single operation.
        
        Args:
            contacts (List[Dict[str, Any]]): A list of contact dictionaries to update or create.
                Each contact must contain at least an 'email' field. Maximum 100 contacts
                per request.
                
                Example contact structure:
                {
                    "email": "user@example.com",
                    "firstName": "John",
                    "lastName": "Doe",
                    "phone": "+1234567890",
                    # ... other contact fields
                }
                
            run_workflow (bool, optional): Whether to trigger associated workflows after
                updating the contacts. Defaults to False.
        
        Returns:
            Dict[str, Any]: Response from the API containing the result of the bulk update
                operation, including success/failure status and any relevant details.
        
        Raises:
            ValidationError: If contacts list is empty, not a list, exceeds 100 items,
                or if any contact is missing the required 'email' field or has an
                invalid email address.
        
        Example:
            >>> contacts_to_update = [
            ...     {"email": "john@example.com", "firstName": "John"},
            ...     {"email": "jane@example.com", "firstName": "Jane"}
            ... ]
            >>> result = client.bulk_update(contacts_to_update, run_workflow=True)
            >>> print(result)
        
        Note:
            - Maximum limit: 100 contacts per request
            - Contacts are identified by email address
            - Existing contacts will be updated; new ones will be created
        """
        logger.info("Bulk updating %d contacts", len(contacts))

        # Validate contacts list is not empty
        if not contacts:
            raise ValidationError("Contacts list cannot be empty.", field="contacts")

        # Validate contacts is a list
        if not isinstance(contacts, list):
            raise ValidationError("Contacts must be a list.", field="contacts")
        
        # Validate maximum limit
        if len(contacts) > 100:
            raise ValidationError(
                "Cannot update more than 100 contacts per request.",
                field="contacts",
                value=len(contacts)
            )

        # Validate each contact has email field and valid email
        for idx, contact in enumerate(contacts):
            if "email" not in contact:
                raise ValidationError(
                    f"Contact at index {idx} must contain an email field.",
                    field="contacts",
                    value=contact,
                )
            self._validate_email(contact["email"])

        # Prepare payload
        payload = {"contacts": contacts, "runWorkflow": run_workflow}

        logger.debug("Bulk update payload validated.")
        
        # Make API request
        return self._client.post("/contacts/bulk-update", data=payload)
    # ---------------------------------------------------------
    # 7. Delete Contact by User ID
    # ---------------------------------------------------------
    def delete_by_user_id(self, user_id: str) -> Any:
        """Delete a contact by user ID.
        
        Permanently deletes a contact identified by the userId field 
        (your application's user identifier).
        
        Args:
            user_id (str): The user identifier to delete. Must be non-empty.
            
        Returns:
            Any: The response from the API delete operation.
            
        Raises:
            ValueError: If user_id is empty or invalid.
            
        Example:
            >>> client.delete_by_user_id("user_12345")
            
        API Endpoint:
            DELETE /contacts/email/userId/{userId}
        """
        logger.info("Deleting contact by user_id: %s", user_id)
        
        self._validate_non_empty(user_id, "user_id")
        
        return self._client.delete(f"/contacts/email/userId/{user_id}")

    # ---------------------------------------------------------
    # 8. Delete Contact by ID
    # ---------------------------------------------------------
    def delete_by_id(self, contact_id: str) -> Any:
        """Delete a contact by its ID.
        
        Deletes a contact from the system using its unique identifier.
        
        Args:
            contact_id (str): The unique identifier of the contact to delete.
                Must be a non-empty string.
        
        Returns:
            Any: The response from the API delete operation.
        
        Raises:
            ValueError: If contact_id is empty or None.
            APIError: If the API request fails.
        
        Example:
            >>> client.delete_by_id("contact_123")
            {'success': True, 'message': 'Contact deleted'}
        
        API Endpoint:
            DELETE https://api.autosend.com/v1/contacts/{id}
        """
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
