import cv2
from app.core.HandProcessor import HandProcessor

detector = HandProcessor()

def detect_fingers(image_path, min_finger_length=30, min_angle=80):
    """
    Detects the number of fingers in an image using the SimpleHandDetector.
    
    Args:
        image_path (str): Path to the image file
        min_finger_length (int): Not used in the new implementation but kept for API compatibility
        min_angle (int): Not used in the new implementation but kept for API compatibility
        
    Returns:
        int: Number of fingers detected (0-5)
    """
    global last_detected_count, hand_skeleton_image
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image from {image_path}")
    
    result_img, fingers = detector.process_image(image)
    
    last_detected_count = fingers
    hand_skeleton_image = result_img
    
    return fingers

def get_last_finger_count():
    """
    Returns the most recent finger count detected.
    
    Returns:
        int: Last detected finger count (0-5)
    """
    return last_detected_count

def detect_hand_skeleton(image_path):
    """
    Uses the SimpleHandDetector to detect hand skeleton and finger count.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        tuple: (finger_count, skeleton_image)
    """
    finger_count = detect_fingers(image_path)
    
    return finger_count, get_hand_skeleton_image()

def get_hand_skeleton_image():
    """
    Returns the latest hand skeleton image.
    
    Returns:
        numpy.ndarray: The image with hand skeleton visualization
    """
    global hand_skeleton_image
    return hand_skeleton_image

def save_debug_image(image_path, output_path="debug_image.jpg"):
    """
    Helper function to save a debug image showing the finger detection process.
    
    Args:
        image_path (str): Path to the input image
        output_path (str): Path to save the debug image
    """
    finger_count = detect_fingers(image_path)
    
    if hand_skeleton_image is not None:
        cv2.imwrite(output_path, hand_skeleton_image)
    else:
        image = cv2.imread(image_path)
        if image is not None:
            cv2.putText(image, f"No hand detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imwrite(output_path, image)