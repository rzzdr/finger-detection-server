from pydantic import BaseModel, Field

class StatusResponse(BaseModel):
    """Response model for status endpoint."""
    status: str = Field(..., description="Server status")
    
    class Config:
        schema_extra = {
            "example": {"status": "online"}
        }