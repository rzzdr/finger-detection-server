from pydantic import BaseModel, Field

class FingerCountResponse(BaseModel):
    """Response model for finger count detection."""
    fingers: int = Field(..., ge=0, le=4, description="Number of fingers detected (0-4)")