from fastapi import APIRouter
from app.models.StatusResponse import StatusResponse

router = APIRouter()

@router.get("/status", response_model=StatusResponse)
async def status():
    """
    A simple health check endpoint to verify the server is running.
    """
    return {"status": "online"}