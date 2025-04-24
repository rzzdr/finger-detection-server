from fastapi import APIRouter

from app.core.finger_detection import get_last_finger_count
from app.models.response_models import FingerCountResponse

router = APIRouter()

@router.get("/current", response_model=FingerCountResponse)
async def get_current_count():
    """
    Returns the most recently detected finger count without requiring a new image upload.
    """
    finger_count = get_last_finger_count()
    return {"fingers": finger_count}