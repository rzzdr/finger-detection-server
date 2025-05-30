from fastapi import APIRouter, File, UploadFile, Query, HTTPException
import os
import uuid

from app.models.FingerCountResponse import FingerCountResponse
from app.utils.image_utils import detect_fingers, detect_hand_skeleton, save_debug_image


router = APIRouter()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)
DEBUG_IMAGE_PATH = os.path.join(TEMP_DIR, "debug_image.jpg")

@router.post("/upload", response_model=FingerCountResponse)
async def upload_image(
    image: UploadFile = File(...),
    min_finger_length: int = Query(30, description="Minimum length to consider as a finger"),
    min_angle: int = Query(80, description="Minimum angle to consider as a finger"),
    use_skeleton: bool = Query(True, description="Whether to use the skeleton detection (True) or contour method (False)")
):
    """
    Receives an image, processes it to detect fingers, and returns the finger count.
    """
    try:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File is not an image")
        
        temp_file_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.jpg")
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await image.read())
        
        if use_skeleton:
            try:
                finger_count, _ = detect_hand_skeleton(temp_file_path)
                save_debug_image(temp_file_path, DEBUG_IMAGE_PATH)
            except Exception as e:
                print(f"Skeleton detection failed: {str(e)}, falling back to contour method")
                finger_count = detect_fingers(
                    temp_file_path, 
                    min_finger_length=min_finger_length,
                    min_angle=min_angle
                )
                save_debug_image(temp_file_path, DEBUG_IMAGE_PATH)
        else:
            finger_count = detect_fingers(
                temp_file_path, 
                min_finger_length=min_finger_length,
                min_angle=min_angle
            )
            save_debug_image(temp_file_path, DEBUG_IMAGE_PATH)
        
        os.remove(temp_file_path)
        
        return {"fingers": finger_count}
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")