# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Edge MCP server extending the core `biosciences-mcp` platform with two specialized tools for competency question (CQ) gap closure:

- **`get_orcs_essentiality`** — CRISPR screen essentiality data from BioGRID ORCS (requires `BIOGRID_API_KEY`)
- **`get_mechanism`** — Mechanism-of-action data from ChEMBL (no auth required)

This is a standalone FastMCP server with no cross-repo import dependencies. Envelope models (`PaginationEnvelope`, `ErrorEnvelope`) are local copies conforming to ADR-001 Section 8.

## Commands

```bash
uv sync --extra dev                          # Install all dependencies
uv run pytest -m unit -v                     # Unit tests (no network)
uv run pytest -m integration -v              # Integration tests (needs network + BIOGRID_API_KEY)
uv run pytest tests/unit/test_mechanism_models.py -v  # Single test file
uv run fastmcp run src/biosciences_mcp_edge/server.py  # Run the MCP server
uv run ruff check --fix . && uv run ruff format .      # Lint and format
uv run pyright                                          # Type checking
```

## Architecture

```
src/biosciences_mcp_edge/
├── server.py              # FastMCP server — tool definitions, error handling, slim mode
├── clients/
│   ├── biogrid_orcs.py    # BioGRID ORCS HTTP client (rate-limited 2 req/s via asyncio lock)
│   └── chembl_mechanism.py  # ChEMBL mechanism HTTP client (CURIE parsing: CHEMBL:NNNNN → CHEMBLNNNNN)
└── models/
    ├── envelopes.py       # PaginationEnvelope[T] and ErrorEnvelope (ADR-001 §8, local copy)
    ├── mechanism.py       # MechanismResult Pydantic model
    └── orcs.py            # OrcsScreenResult Pydantic model
```

**Data flow**: Tool function (server.py) → client function (clients/) → external API → Pydantic model → envelope wrapper → return to caller.

**Error handling pattern**: Clients raise exceptions (`ValueError`, `httpx.HTTPStatusError`, `httpx.HTTPError`); server.py catches them and returns typed `ErrorEnvelope` responses with `ErrorCode` enum values (`UNRESOLVED_ENTITY`, `ENTITY_NOT_FOUND`, `RATE_LIMITED`, `UPSTREAM_ERROR`).

**CURIE convention**: ChEMBL tools accept both `CHEMBL:225072` (CURIE) and `CHEMBL225072` (raw) formats. BioGRID ORCS uses Entrez gene IDs (integers).

## Key Conventions

- `asyncio_mode = "auto"` — all async test functions run automatically without explicit event loop fixtures
- `slim` parameter on tools nulls out optional fields to reduce response payload
- Tests use `@pytest.mark.unit` and `@pytest.mark.integration` markers; integration tests requiring `BIOGRID_API_KEY` use the `biogrid_api_key` fixture from `conftest.py` which skips when the key is absent
- Ruff configured for Python 3.11, line length 100
