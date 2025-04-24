from fastapi import APIRouter

from app.models.FingerCountResponse import FingerCountResponse
from app.utils.image_utils import get_last_finger_count

router = APIRouter()

@router.get("/current", response_model=FingerCountResponse)
async def get_current_count():
    """
    Returns the most recently detected finger count without requiring a new image upload.
    """
    finger_count = get_last_finger_count()
    return {"fingers": finger_count}