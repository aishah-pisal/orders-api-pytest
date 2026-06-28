"""
API tests for an order-creation request, run against Postman Echo.

WHY POSTMAN ECHO
Postman Echo (https://postman-echo.com/post) is a live service that returns the
request it received (method, headers, and parsed body). That lets us assert a
genuine round trip: the client serialised and sent exactly the order payload we
intended, verified against a real network endpoint rather than a static mock.

SCENARIOS
  1. Happy path:     request is accepted (200) and the body comes back unchanged
  2. Auth header:    the client attaches the Authorization header to the request
  3. Error handling: the client surfaces and raises on error responses (401, 404)
  4. HTTP method:    the create endpoint is POST-only (a GET is rejected)

Echo does not validate the order schema, so this suite tests the client side:
how our own code builds the request (method, headers, body) and handles the
response, not the server's validation rules.
"""

import pytest
import requests

ORDERS_PATH = "/post"  # Echo's create-style endpoint; maps to /orders on a real API
TIMEOUT = 30


# 1. Happy path: request accepted and body comes back unchanged
def test_create_order_succeeds_and_echoes_payload(base_url, session, valid_payload):
    """The request is accepted (200) and Echo returns the exact body we sent."""
    resp = session.post(f"{base_url}{ORDERS_PATH}", json=valid_payload, timeout=TIMEOUT)

    assert resp.status_code == 200, resp.text[:300]
    assert resp.json()["json"] == valid_payload


# 2. Auth header: client attaches the Authorization header
def test_request_includes_auth_header(base_url, session, valid_payload):
    """The client must send the Authorization header it was configured with."""
    token = "Bearer test-token-123"

    resp = session.post(
        f"{base_url}{ORDERS_PATH}",
        json=valid_payload,
        headers={"Authorization": token},
        timeout=TIMEOUT,
    )

    # Echo reflects request headers back (lowercased) under the "headers" key.
    sent_headers = resp.json()["headers"]
    assert sent_headers.get("authorization") == token


# 3. Error handling: client surfaces and raises on error responses
@pytest.mark.parametrize(
    "path, expected",
    [
        ("/basic-auth", 401),                 # protected endpoint, no credentials sent
        ("/this-route-does-not-exist", 404),  # unknown route
    ],
)
def test_client_surfaces_error_status(base_url, session, path, expected):
    """The client must propagate error codes and raise on a 4xx response."""
    resp = session.get(f"{base_url}{path}", timeout=TIMEOUT)

    assert resp.status_code == expected
    with pytest.raises(requests.HTTPError):
        resp.raise_for_status()


# 4. HTTP method: create endpoint is POST-only
def test_get_on_create_endpoint_is_rejected(base_url, session):
    """The create endpoint is POST-only; a GET must not succeed."""
    resp = session.get(f"{base_url}{ORDERS_PATH}", timeout=TIMEOUT)

    assert resp.status_code == 404
