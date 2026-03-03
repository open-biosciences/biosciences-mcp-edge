"""ChEMBL mechanism-of-action client.

Base URL: https://www.ebi.ac.uk/chembl/api/data
Auth: None required
Rate limit: 10 req/s (generous; no enforced throttle needed)
"""

import re

import httpx

from biosciences_mcp_edge.models.mechanism import MechanismResult

BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

_CURIE_PATTERN = re.compile(r"^CHEMBL:(\d+)$", re.IGNORECASE)


def parse_chembl_curie(chembl_id: str) -> str:
    """Convert CHEMBL:NNNNN CURIE to CHEMBLNNNNN for API call.

    Accepts both 'CHEMBL:12345' and 'CHEMBL12345' formats.
    """
    match = _CURIE_PATTERN.match(chembl_id)
    if match:
        return f"CHEMBL{match.group(1)}"
    # Already in CHEMBLNNNNN format
    if chembl_id.upper().startswith("CHEMBL") and chembl_id[6:].isdigit():
        return chembl_id.upper()
    raise ValueError(f"Invalid ChEMBL identifier: '{chembl_id}'. Expected CHEMBL:NNNNN or CHEMBLNNNNN.")


async def get_mechanisms(chembl_id: str) -> list[MechanismResult]:
    """Fetch mechanism-of-action data for a ChEMBL compound.

    Args:
        chembl_id: ChEMBL CURIE (e.g. 'CHEMBL:225072') or raw ID ('CHEMBL225072').

    Returns:
        List of MechanismResult objects.
    """
    api_id = parse_chembl_curie(chembl_id)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{BASE_URL}/mechanism.json",
            params={"molecule_chembl_id": api_id},
        )
        resp.raise_for_status()
        data = resp.json()

    mechanisms = data.get("mechanisms", [])
    return [
        MechanismResult(
            mechanism_of_action=m.get("mechanism_of_action"),
            target_name=m.get("target_pref_name") or m.get("target_name"),
            target_chembl_id=m.get("target_chembl_id"),
            action_type=m.get("action_type"),
            direct_interaction=m.get("direct_interaction"),
            max_phase=m.get("max_phase"),
            molecule_chembl_id=m.get("molecule_chembl_id"),
        )
        for m in mechanisms
    ]
