"""Shared test fixtures."""

import os

import pytest


@pytest.fixture
def biogrid_api_key() -> str:
    """Get BIOGRID_API_KEY or skip."""
    key = os.environ.get("BIOGRID_API_KEY")
    if not key:
        pytest.skip("BIOGRID_API_KEY not set")
    return key
