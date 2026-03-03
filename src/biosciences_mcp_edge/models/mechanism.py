"""ChEMBL mechanism-of-action result model."""

from pydantic import BaseModel


class MechanismResult(BaseModel):
    """A single mechanism-of-action record from ChEMBL."""

    mechanism_of_action: str | None = None
    target_name: str | None = None
    target_chembl_id: str | None = None
    action_type: str | None = None
    direct_interaction: bool | None = None
    max_phase: int | None = None
    molecule_chembl_id: str | None = None
