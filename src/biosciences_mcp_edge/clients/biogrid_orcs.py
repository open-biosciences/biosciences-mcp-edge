"""BioGRID ORCS CRISPR screen client.

Base URL: https://orcsws.thebiogrid.org
Auth: BIOGRID_API_KEY env var
Rate limit: 2 req/s (enforced via asyncio lock + sleep)
"""

import asyncio
import os
import time

import httpx

from biosciences_mcp_edge.models.orcs import OrcsScreenResult

BASE_URL = "https://orcsws.thebiogrid.org"

_lock = asyncio.Lock()
_last_request_time: float = 0.0
_MIN_INTERVAL = 0.5  # 2 req/s


async def _rate_limit() -> None:
    """Enforce 2 req/s rate limit."""
    global _last_request_time
    async with _lock:
        now = time.monotonic()
        elapsed = now - _last_request_time
        if elapsed < _MIN_INTERVAL:
            await asyncio.sleep(_MIN_INTERVAL - elapsed)
        _last_request_time = time.monotonic()


def _get_api_key() -> str | None:
    return os.environ.get("BIOGRID_API_KEY")


async def get_essentiality(
    entrez_id: int,
    hit_only: bool = True,
) -> list[OrcsScreenResult]:
    """Fetch ORCS essentiality data for a gene by Entrez ID.

    Args:
        entrez_id: NCBI Entrez gene ID (e.g. 7298 for TYMS).
        hit_only: If True, only return screens where the gene was a hit.

    Returns:
        List of OrcsScreenResult objects.
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("BIOGRID_API_KEY environment variable is not set")

    params: dict[str, str] = {
        "accesskey": api_key,
        "format": "json",
    }
    if hit_only:
        params["hit"] = "yes"

    await _rate_limit()

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{BASE_URL}/gene/{entrez_id}", params=params)
        resp.raise_for_status()
        data = resp.json()

    # API returns a flat list of records, each with SCREEN_ID, SCORE.1, HIT, etc.
    if not isinstance(data, list):
        data = [data]

    results: list[OrcsScreenResult] = []
    for rec in data:
        if not isinstance(rec, dict):
            continue
        results.append(
            OrcsScreenResult(
                screen_id=int(rec.get("SCREEN_ID", 0)),
                score=_safe_float(rec.get("SCORE.1")),
                hit=rec.get("HIT", "NO"),
                source_id=None,  # Not in gene endpoint; available via /screens/
                cell_line=None,  # Not in gene endpoint; available via /screens/
                phenotype=None,  # Not in gene endpoint; available via /screens/
                scoring_method=None,  # Not in gene endpoint; available via /screens/
            )
        )

    return results


def _safe_float(val: object) -> float | None:
    if val is None or val == "" or val == "N/A":
        return None
    try:
        return float(val)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None
