"""Integration tests for ORCS API (requires BIOGRID_API_KEY)."""

import pytest

from biosciences_mcp_edge.clients.biogrid_orcs import get_essentiality


@pytest.mark.integration
async def test_tyms_essentiality(biogrid_api_key: str) -> None:
    """TYMS (Entrez 7298) should have ORCS screen data."""
    results = await get_essentiality(7298, hit_only=True)
    assert len(results) > 0
    for r in results:
        assert r.hit == "YES"
        assert r.screen_id > 0


@pytest.mark.integration
async def test_tyms_all_screens(biogrid_api_key: str) -> None:
    """TYMS should have many screens when not filtering by hit."""
    results = await get_essentiality(7298, hit_only=False)
    assert len(results) > 10  # TYMS is well-studied
