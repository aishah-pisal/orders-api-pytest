# Test Plan & Cases: `POST /api/orders`

This is the test design for the order-creation endpoint. It describes what a
real, validating orders API should do. The automated suite in `tests/` covers the
subset that can be verified against Postman Echo (see "Automated?" below).

## API Endpoint

```
POST /api/orders
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "store_id": <integer>,
  "items": [
    { "product_id": <integer>, "quantity": <integer>,
      "customizations": { "size": "<string>", "milk": "<string>" } }
  ],
  "payment_method_id": <integer>
}
```

## Test Cases

| ID | Type | What it sends | Expected | Automated? |
|----|------|---------------|----------|------------|
| TC-001 | Happy path | Valid order with customizations, valid token | 201 Created, order saved | Yes |
| TC-002 | Authentication | No `Authorization` header | 401 Unauthorized | Yes |
| TC-003 | Authentication | Expired or invalid token | 401 Unauthorized | Yes |
| TC-004 | Validation | Missing required `payment_method_id` | 400 Bad Request | No |
| TC-005 | Boundary | `quantity` of 0 | 400 Bad Request | No |
| TC-006 | Customizations | `milk` value not on the allowed list | 400 Bad Request | No |
| TC-007 | Resource | `product_id` that does not exist | 404 Not Found | No |
| TC-008 | Business rule | Product is out of stock | 409 Conflict | No |
| TC-009 | Business rule | Payment is declined by the processor | 402 Payment Required, order not confirmed | No |
| TC-010 | Partial failure | Two items, one out of stock | 409, whole order rejected atomically (nothing charged, no stock changed) | No |
| TC-011 | Authentication | Valid token attached | 201 Created, request authorised | Yes |
| TC-012 | HTTP method | GET sent to a POST-only endpoint | 405 Method Not Allowed | Yes |

## Test Types

**Happy path (TC-001)** is the baseline: a fully correct request succeeds. Every
other case breaks one thing on purpose.

**Authentication (TC-002, TC-003, TC-011)** covers the three token states: missing,
invalid, and valid. A broken auth layer can fail in any of them.

**Validation (TC-004, TC-005, TC-006)** checks the server inspects the body before
acting: required fields are required, numbers must be sensible (0 is a boundary
value), and constrained fields are checked against an allowed set.

**Resource (TC-007)** is a well-formed request that names something which does not
exist. Syntactically fine, semantically wrong.

**Business rules (TC-008, TC-009, TC-010)** are the cases where the request is
valid but real-world conditions block it. TC-010 is the important one: it checks
the order is all-or-nothing, so a multi-item order never half-completes.

**HTTP method (TC-012)** checks the endpoint follows HTTP conventions, independent
of any order logic.

## Automation Coverage

Postman Echo is a mirror: it sends the request back and always returns success. 
As of now, it won't checks whether the data is valid, as it has no idea what
an order is.

The four automated cases work against a mirror because they only check what our
own code does: did it build the request correctly (TC-001, TC-011), and did it
handle an error response correctly (TC-002/003, TC-012). Echo can show us that.

The other eight need the server to look at the data and say "no" (reject a missing
field, a bad quantity, an out-of-stock product, a declined payment). Echo never
says no, so a test like "send quantity 0, expect 400" would fail, because Echo
accepts everything. They are not automated here for that reason. Point the suite at
a real API that does validate and they would run and pass; only the URL and the
expected error codes would change.

One detail on TC-012: a real API has an /orders route that exists but only
allows POST, so a GET returns 405 Method Not Allowed. Echo has no GET route at
that path at all, so it sees no matching route and returns 404 Not Found. Both
reject the GET; it is "not found" on Echo rather than "method not allowed" simply
because the route is not defined there.
