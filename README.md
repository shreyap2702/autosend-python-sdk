# Autosend Python SDK

Lightweight Python client for the Autosend API. This SDK provides a thin, well documented wrapper around Autosend's HTTP endpoints for managing contacts and sending emails.

## Features

- Easy authentication with an API key
- Contact management: create, upsert, remove, search, bulk update, delete
- Sending: transactional single sends and bulk sends with template/dynamic data support
- Input validation and clear, typed exceptions

## Installation

Install from source (recommended for development):

```bash
pip install -e .
```

Install directly from GitHub (replace <owner> with the repository owner if published):

```bash
pip install git+https://github.com/shreyap2702/autosend-python-sdk.git
```

Install from PyPI

```bash
pip install autosend-shreya-sdk
```

Notes:
- The project uses `requests` for HTTP; it will be installed automatically from `pyproject.toml`.

## Quickstart

1. Create a client with your API key.

```python
from autosend.client import AutosendClient

client = AutosendClient(api_key="YOUR_API_KEY")
```

2. Use resource helpers to manage contacts or send emails.

```python
# Contacts
client.contacts.create_contact(
	email="jane.doe@example.com",
	first_name="Jane",
	last_name="Doe",
	user_id="user_123",
	custom_fields={"company": "Acme"}
)

# Sending a single transactional email
client.sending.send_email(
	to_email="jane.doe@example.com",
	to_name="Jane Doe",
	from_email="noreply@company.com",
	from_name="Company",
	subject="Welcome!",
	html="<h1>Hello {{name}}</h1>",
	dynamic_data={"name": "Jane"}
)
```

## Contact API examples

- Create contact: `client.contacts.create_contact(...)`
- Upsert contact: `client.contacts.upsert_contact(...)` (creates or updates by email)
- Remove contacts: `client.contacts.remove_contacts([emails])`
- Get contact: `client.contacts.get_contact(contact_id)`
- Search by emails: `client.contacts.search_by_emails([emails])`
- Bulk update: `client.contacts.bulk_update(contacts_list, run_workflow=False)`
- Delete by user ID: `client.contacts.delete_by_user_id(user_id)`
- Delete by contact ID: `client.contacts.delete_by_id(contact_id)`

Refer to the docstrings in `autosend/resources/contacts.py` for parameter details and examples.

## Sending API examples

- Send a single email: `client.sending.send_email(...)` — supports attachments, reply-to, unsubscribe options, and template dynamic data.
- Send bulk emails: `client.sending.send_bulk(recipients=..., ...)` — up to 100 recipients per request.

Refer to `autosend/resources/sending.py` for payload and validation rules.

## Configuration

- api_key (required): pass to `AutosendClient(api_key=...)`
- base_url (optional): pass `base_url="https://api.autosend.com/v1"` to target a custom endpoint or mock server.

## Error handling

The SDK raises typed exceptions from `autosend.errors`:

- `AutosendError` — base class for SDK errors
- `AuthenticationError` — invalid or missing API key (401)
- `RequestError` — network or request-level failures
- `ValidationError` — invalid input/arguments

Example:

```python
from autosend.client import AutosendClient
from autosend.errors import AutosendError, ValidationError

client = AutosendClient(api_key="YOUR_API_KEY")
try:
	client.contacts.create_contact(email="bad-email", first_name="", last_name="")
except ValidationError as e:
	print("Validation failed:", e)
except AutosendError as e:
	print("Autosend API error:", e)
```
