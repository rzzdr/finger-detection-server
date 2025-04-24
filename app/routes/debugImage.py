from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

# Import the constant directly to avoid circular import
TEMP_DIR = "temp"
DEBUG_IMAGE_PATH = os.path.join(TEMP_DIR, "debug_image.jpg")

router = APIRouter()

@router.get("/debug-image")
async def get_debug_image():
    """
    Returns the latest debug image showing finger detection visualization.
    Used by the client to display finger skeleton.
    """
    if os.path.exists(DEBUG_IMAGE_PATH):
        return FileResponse(DEBUG_IMAGE_PATH)
    else:
        raise HTTPException(status_code=404, detail="Debug image not available")