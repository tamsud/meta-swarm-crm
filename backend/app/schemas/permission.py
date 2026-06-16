"""Permission schemas - read-only response only (no Create/Update/Delete)."""

from pydantic import BaseModel, ConfigDict


class PermissionResponse(BaseModel):
    """Response schema for a permission entry.

    No Create/Update/Delete schemas exist, reinforcing the read-only contract
    at the type level.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    module: str
    action: str
    description: str
