"""Unit tests for ORCS models."""

import pytest

from biosciences_mcp_edge.models.orcs import OrcsScreenResult


@pytest.mark.unit
class TestOrcsScreenResult:
    def test_minimal(self) -> None:
        result = OrcsScreenResult(screen_id=213, hit="YES")
        assert result.screen_id == 213
        assert result.hit == "YES"
        assert result.score is None
        assert result.cell_line is None

    def test_full(self) -> None:
        result = OrcsScreenResult(
            screen_id=213,
            score=-0.377,
            hit="YES",
            source_id=29083409,
            cell_line="786-O",
            phenotype="viability",
            scoring_method="CERES",
        )
        assert result.screen_id == 213
        assert result.score == pytest.approx(-0.377)
        assert result.hit == "YES"
        assert result.source_id == 29083409
        assert result.cell_line == "786-O"
        assert result.phenotype == "viability"
        assert result.scoring_method == "CERES"

    def test_serialization_roundtrip(self) -> None:
        result = OrcsScreenResult(screen_id=511, score=-0.556, hit="YES", cell_line="Caki-1")
        data = result.model_dump()
        restored = OrcsScreenResult.model_validate(data)
        assert restored == result
