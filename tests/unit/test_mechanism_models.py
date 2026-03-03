"""Unit tests for mechanism models and CURIE parsing."""

import pytest

from biosciences_mcp_edge.clients.chembl_mechanism import parse_chembl_curie
from biosciences_mcp_edge.models.mechanism import MechanismResult


@pytest.mark.unit
class TestMechanismResult:
    def test_minimal(self) -> None:
        result = MechanismResult()
        assert result.mechanism_of_action is None
        assert result.target_name is None

    def test_full(self) -> None:
        result = MechanismResult(
            mechanism_of_action="Thymidylate synthase inhibitor",
            target_name="Thymidylate synthase",
            target_chembl_id="CHEMBL1898",
            action_type="INHIBITOR",
            direct_interaction=True,
            max_phase=4,
            molecule_chembl_id="CHEMBL225072",
        )
        assert result.mechanism_of_action == "Thymidylate synthase inhibitor"
        assert result.action_type == "INHIBITOR"
        assert result.max_phase == 4

    def test_serialization_roundtrip(self) -> None:
        result = MechanismResult(
            mechanism_of_action="TYMS inhibitor",
            target_chembl_id="CHEMBL1898",
            molecule_chembl_id="CHEMBL225072",
        )
        data = result.model_dump()
        restored = MechanismResult.model_validate(data)
        assert restored == result


@pytest.mark.unit
class TestParseChemblCurie:
    def test_curie_format(self) -> None:
        assert parse_chembl_curie("CHEMBL:225072") == "CHEMBL225072"

    def test_raw_format(self) -> None:
        assert parse_chembl_curie("CHEMBL225072") == "CHEMBL225072"

    def test_lowercase_curie(self) -> None:
        assert parse_chembl_curie("chembl:225072") == "CHEMBL225072"

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid ChEMBL identifier"):
            parse_chembl_curie("not-a-chembl-id")

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid ChEMBL identifier"):
            parse_chembl_curie("")
