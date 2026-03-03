"""ORCS CRISPR screen result model."""

from pydantic import BaseModel


class OrcsScreenResult(BaseModel):
    """A single CRISPR screen result from BioGRID ORCS."""

    screen_id: int
    score: float | None = None
    hit: str  # "YES" or "NO"
    source_id: int | None = None  # PubMed ID
    cell_line: str | None = None
    phenotype: str | None = None
    scoring_method: str | None = None
