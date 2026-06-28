"""Shared pytest fixtures for the Postman Echo order tests."""

import os

import pytest
import requests

# Overridable so the same suite can run against Postman Echo, a staging server,
# or a local instance without touching the test code.
DEFAULT_BASE_URL = "https://postman-echo.com"
REQUEST_TIMEOUT = 30  # seconds


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("ECHO_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


@pytest.fixture(scope="session")
def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})
    yield s
    s.close()


@pytest.fixture()
def valid_payload() -> dict:
    """A well-formed order request body."""
    return {
        "address": "123 Market Street, Springfield",
        "item": {
            "itemId": 1,
            "name": "Wireless Mouse",
            "price": 25,
            "description": "Ergonomic wireless mouse",
        },
    }
