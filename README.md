# biosciences-mcp-edge

Edge MCP tools that extend the core biosciences-mcp server with specialized endpoints for CQ gap closure.

## Tools

| Tool | Source API | Auth | Description |
|------|-----------|------|-------------|
| `get_orcs_essentiality` | BioGRID ORCS | `BIOGRID_API_KEY` | CRISPR screen essentiality data by Entrez gene ID |
| `get_mechanism` | ChEMBL | None | Mechanism-of-action data by ChEMBL compound ID |

## Setup

```bash
uv sync --extra dev
cp .env.example .env  # Add your BIOGRID_API_KEY
```

## Run

```bash
uv run fastmcp run src/biosciences_mcp_edge/server.py
```

## Test

```bash
uv run pytest -m unit -v
uv run pytest -m integration -v  # requires BIOGRID_API_KEY
```
