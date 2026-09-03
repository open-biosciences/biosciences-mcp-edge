# ADRs — inherited from biosciences-mcp, with one recorded departure

`biosciences-mcp-edge` extends the `biosciences-mcp` platform (see `CLAUDE.md`: "Edge MCP
server extending the core biosciences-mcp platform"). It follows that platform's ADRs and
does not restate them. The binding copies are in
[`open-biosciences/biosciences-mcp/docs/adr/accepted/`](https://github.com/open-biosciences/biosciences-mcp/tree/main/docs/adr/accepted).
The placement rule for the org is in
[`biosciences-program/docs/adr/README.md`](https://github.com/open-biosciences/biosciences-program/blob/main/docs/adr/README.md).

| ADR | Mandate | How it applies here |
|---|---|---|
| **001 §3** Fuzzy-to-Fact | Phase 1 natural-language search returns ranked candidates; Phase 2 accepts only resolved CURIEs | **Departed from by design.** See below. |
| **001 §4** Agentic Biolink | Flat JSON; `cross_references` per the Key Registry | Flat JSON adopted. Results are per-screen and per-mechanism records keyed by the caller's identifier; they carry no `cross_references` object because the entity they describe was resolved upstream by the caller. |
| **001 §7** Token budgeting | `slim=True` on list tools | Adopted: both tools take `slim`. |
| **001 §8** Canonical envelopes | Exact pagination and error shapes | Adopted verbatim as local copies in `models/envelopes.py` (no cross-repo import by design). Error codes from ADR-001 Appendix B: `UNRESOLVED_ENTITY`, `ENTITY_NOT_FOUND`, `RATE_LIMITED`, `UPSTREAM_ERROR`. |
| **004** Lifecycle | Module-level singleton; `@mcp.on_event` forbidden | Adopted (`server.py`). |
| **007** Gateway rate resilience | Full-jitter backoff on platform constants; `Retry-After` precedence; headerless-throttle handling; `RATE_LIMITED` reported, never swallowed | **Partially adopted.** `clients/biogrid_orcs.py` enforces a 2 req/s interval with an `asyncio.Lock` and returns `RATE_LIMITED` on 429, but has no retry or backoff; `clients/chembl_mechanism.py` has no throttle. Adoption of the platform base client or a verbatim copy is the follow-up named in ADR-007 §4 item 4. |
| 002, 003, 005, 006 | Skills, Spec Kit SDLC, worktrees, single-writer package | Not applicable at this repo's size (two tools, no package split, no parallel connectors). |

## The departure: no Fuzzy-to-Fact phase

ADR-001 §3 requires every entity lookup to go through a fuzzy search that returns candidates
before a strict lookup by CURIE. This repo has no search tools. Both tools are **strict
retrievals keyed by an identifier the caller already resolved** through the platform servers:

- `get_orcs_essentiality(entrez_id: int, hit_only, slim)` — CRISPR screen essentiality from
  BioGRID ORCS for an Entrez gene ID obtained from `hgnc_get_gene` or `entrez_get_gene`.
- `get_mechanism(chembl_id: str, slim)` — mechanism of action from ChEMBL for a `CHEMBL:NNNN`
  CURIE (bare `CHEMBLNNNN` also accepted) obtained from `chembl_search_compounds`.

The reason is the division of labour between the two repos. The `biosciences-mcp` tools give an
agent context-light node retrieval so it can **build** a graph itself rather than consume and
filter a large one. The edge tools are the **detailed retrievals performed after that graph
exists**, and deterministic wrappers for retrievals that skills previously performed
non-deterministically over raw APIs. Putting a fuzzy phase in front of them would duplicate
resolution the platform servers already did. Free-text input to either tool returns
`UNRESOLVED_ENTITY` with a recovery hint naming the platform search tool, which is the §3
failure mode without the §3 search phase.

Recorded 2026-09-03 under AGE-689.
