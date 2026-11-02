"""Global pytest configuration and shared fixtures for FieldCheck test suite."""

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Ensure anyio defaults to asyncio for all async test cases."""
    return "asyncio"
