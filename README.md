# Order API tests (Postman Echo)

A small pytest + requests suite for an order-creation endpoint, run against a live
service ([Postman Echo](https://postman-echo.com)) instead of a static mock.

The order schema under test:

```json
{
  "address": "<string>",
  "item": {
    "itemId": <integer>,
    "name": "<string>",
    "price": <integer>,
    "description": "<string>"
  }
}
```

## What the suite checks

| Scenario | Test | Verifies |
|----------|------|----------|
| Happy path | `test_create_order_succeeds_and_echoes_payload` | Accepted (200) and the body survives the round trip |
| Auth header | `test_request_includes_auth_header` | Client attaches the `Authorization` header to the request |
| Error handling | `test_client_surfaces_error_status` | Client propagates and raises on error responses (401, 404) |
| HTTP method | `test_get_on_create_endpoint_is_rejected` | Create endpoint is POST-only (GET → 404) |

## Scope: what this does and doesn't test

Echo does not validate the order schema, so this suite tests the **client side**:
how our own code builds the request and handles the response. Specifically it
checks that the request is constructed correctly (right method, headers, and JSON
body), that the body comes back unchanged, that the `Authorization` header is
attached, and that the client reacts correctly when it gets an error response.

It does **not** test server-side validation, because Echo has none. A real API
would reject a missing `address` or a non-integer `price`; Echo just reflects back
whatever you send. The error-handling test does see real 401 and 404 responses,
but those come from Echo's own endpoints (its auth endpoint and an unknown route),
not from any check on the order itself.

Keeping these two things apart, what the client does versus what the server
enforces, is the main design decision here.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

All tests should pass against Echo. Point at a different host without code changes:

```bash
ECHO_BASE_URL=https://staging.example.com pytest
```

## Layout

```
.
├── tests/
│   ├── conftest.py        # base_url, session, valid_payload fixtures
│   └── test_orders.py
├── requirements.txt
├── pytest.ini
└── .github/workflows/api-tests.yml   # runs pytest on push / PR
```

