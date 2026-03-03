"""Biosciences MCP Edge server — ORCS essentiality and ChEMBL mechanism tools."""

import httpx
from fastmcp import FastMCP

from biosciences_mcp_edge.clients import biogrid_orcs, chembl_mechanism
from biosciences_mcp_edge.models.envelopes import ErrorEnvelope, PaginationEnvelope
from biosciences_mcp_edge.models.mechanism import MechanismResult
from biosciences_mcp_edge.models.orcs import OrcsScreenResult

mcp = FastMCP(
    "biosciences-mcp-edge",
    instructions=(
        "Edge MCP tools for ORCS CRISPR screen essentiality and ChEMBL mechanism-of-action. "
        "Use get_orcs_essentiality with an Entrez gene ID to check CRISPR screen hits. "
        "Use get_mechanism with a ChEMBL CURIE (CHEMBL:NNNNN) to get mechanism-of-action data."
    ),
)


@mcp.tool()
async def get_orcs_essentiality(
    entrez_id: int,
    hit_only: bool = True,
    slim: bool = False,
) -> PaginationEnvelope[OrcsScreenResult] | ErrorEnvelope:
    """Get CRISPR screen essentiality data from BioGRID ORCS.

    Args:
        entrez_id: NCBI Entrez gene ID (e.g. 7298 for TYMS, 1723 for DHODH).
        hit_only: If True, only return screens where the gene was scored as a hit.
        slim: If True, return fewer fields per result.

    Returns:
        PaginationEnvelope with OrcsScreenResult items, or ErrorEnvelope on failure.
    """
    try:
        results = await biogrid_orcs.get_essentiality(entrez_id, hit_only=hit_only)
    except ValueError as e:
        return ErrorEnvelope.unresolved_entity(str(e))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return ErrorEnvelope.rate_limited()
        return ErrorEnvelope.upstream_error(e.response.status_code, str(e))
    except httpx.HTTPError as e:
        return ErrorEnvelope.upstream_error(0, str(e))

    if not results:
        return ErrorEnvelope.entity_not_found(str(entrez_id))

    if slim:
        for r in results:
            r.phenotype = None
            r.scoring_method = None

    return PaginationEnvelope.create(items=results, total_count=len(results))


@mcp.tool()
async def get_mechanism(
    chembl_id: str,
    slim: bool = False,
) -> PaginationEnvelope[MechanismResult] | ErrorEnvelope:
    """Get mechanism-of-action data from ChEMBL.

    Args:
        chembl_id: ChEMBL CURIE (e.g. 'CHEMBL:225072' for Pemetrexed) or raw ID ('CHEMBL225072').
        slim: If True, return fewer fields per result.

    Returns:
        PaginationEnvelope with MechanismResult items, or ErrorEnvelope on failure.
    """
    try:
        results = await chembl_mechanism.get_mechanisms(chembl_id)
    except ValueError as e:
        return ErrorEnvelope.unresolved_entity(str(e))
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return ErrorEnvelope.rate_limited()
        return ErrorEnvelope.upstream_error(e.response.status_code, str(e))
    except httpx.HTTPError as e:
        return ErrorEnvelope.upstream_error(0, str(e))

    if not results:
        return ErrorEnvelope.entity_not_found(
            chembl_id,
            recovery_hint=(
                "The identifier is valid but ChEMBL has no mechanism-of-action data for this compound. "
                "Try PubMed literature or DrugBank for mechanism information."
            ),
        )

    if slim:
        for r in results:
            r.direct_interaction = None

    return PaginationEnvelope.create(items=results, total_count=len(results))
