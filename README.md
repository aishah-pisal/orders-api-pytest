# Order API Tests (Postman Echo)

A small pytest + requests suite for an order-creation endpoint, run against a live
service ([Postman Echo](https://postman-echo.com)).

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

These four cover the client side: how the code builds the request and handles the
response. Server-side validation and business rules are out of scope here (Echo
does not validate), and are documented in
[`docs/TEST_PLAN_AND_CASES.md`](docs/TEST_PLAN_AND_CASES.md) along with the fuller
12-test cases design.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

## Layout

```
.
├── tests/
│   ├── conftest.py        # base_url, session, valid_payload fixtures
│   └── test_orders.py
├── docs/
│   └── TEST_PLAN_AND_CASES.md   # full 12-case design; 4 are automated here
├── requirements.txt
├── pytest.ini
└── .github/workflows/api-tests.yml   # runs pytest on push / PR
```

