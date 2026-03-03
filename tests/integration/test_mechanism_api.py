"""Integration tests for ChEMBL mechanism API (public, no key required)."""

import pytest

from biosciences_mcp_edge.clients.chembl_mechanism import get_mechanisms


@pytest.mark.integration
async def test_pemetrexed_mechanism() -> None:
    """Pemetrexed (CHEMBL:225072) should be a TYMS inhibitor."""
    results = await get_mechanisms("CHEMBL:225072")
    assert len(results) > 0
    moa_texts = [r.mechanism_of_action for r in results if r.mechanism_of_action]
    assert any("thymidylate synthase" in m.lower() for m in moa_texts), (
        f"Expected TYMS-related mechanism, got: {moa_texts}"
    )


@pytest.mark.integration
async def test_mechanism_raw_id() -> None:
    """Should also accept raw CHEMBL ID format."""
    results = await get_mechanisms("CHEMBL225072")
    assert len(results) > 0


@pytest.mark.integration
async def test_mechanism_nonexistent() -> None:
    """A non-existent compound should return empty list."""
    results = await get_mechanisms("CHEMBL:999999999")
    assert results == []
