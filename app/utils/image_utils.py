import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def read_image_file_to_cv2(file_path):
    """
    Reads an image file and returns an OpenCV image.
    
    Args:
        file_path (str): Path to the image file
    
    Returns:
        numpy.ndarray: OpenCV image
    """
    return cv2.imread(file_path)

def bytes_to_cv2_image(image_bytes):
    """
    Converts bytes to an OpenCV image.
    
    Args:
        image_bytes (bytes): Image data as bytes
    
    Returns:
        numpy.ndarray: OpenCV image
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    
    # Decode the numpy array as an image
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def cv2_to_base64(image):
    """
    Converts an OpenCV image to base64 string.
    
    Args:
        image (numpy.ndarray): OpenCV image
    
    Returns:
        str: Base64 encoded string
    """
    # Convert OpenCV image to PIL Image
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    
    # Save PIL Image to BytesIO object
    buffer = BytesIO()
    pil_image.save(buffer, format="JPEG")
    
    # Encode BytesIO to base64
    img_str = base64.b64encode(buffer.getvalue()).decode('ascii')
    
    return img_str