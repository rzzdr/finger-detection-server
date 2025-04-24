import cv2
import numpy as np
import os

# Global variable to store the most recent finger count
last_detected_count = 0
hand_skeleton_image = None

class SimpleHandDetector:
    def __init__(self):
        pass
        
    def detect_skin(self, img):
        """Detect skin using HSV color space"""
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define skin color ranges (more inclusive)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Second range for skin detection (to cover more skin tones)
        lower_skin2 = np.array([170, 20, 70], dtype=np.uint8)
        upper_skin2 = np.array([180, 255, 255], dtype=np.uint8)
        
        # Combine masks
        mask1 = cv2.inRange(hsv, lower_skin, upper_skin)
        mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
        skin_mask = cv2.bitwise_or(mask1, mask2)
        
        # Clean up mask with morphological operations
        kernel = np.ones((5, 5), np.uint8)
        skin_mask = cv2.dilate(skin_mask, kernel, iterations=2)
        skin_mask = cv2.erode(skin_mask, kernel, iterations=1)
        skin_mask = cv2.GaussianBlur(skin_mask, (5, 5), 0)
        
        return skin_mask
    
    def get_hand_contour(self, mask):
        """Extract the largest contour from the mask"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
            
        # Find the largest contour
        max_contour = max(contours, key=cv2.contourArea)
        
        # Only return if contour is large enough (to filter noise)
        if cv2.contourArea(max_contour) > 5000:
            return max_contour
        
        return None
    
    def count_fingers(self, contour, img):
        """Count fingers from contour using convex hull method"""
        if contour is None:
            return img, 0
            
        # Create output image (for visualization)
        output = img.copy()
        
        # Draw contour
        cv2.drawContours(output, [contour], -1, (0, 255, 0), 2)
        
        # Get convex hull
        hull = cv2.convexHull(contour, returnPoints=False)
        
        # Calculate convexity defects
        try:
            defects = cv2.convexityDefects(contour, hull)
        except:
            return output, 0
            
        if defects is None:
            return output, 0
            
        # Count fingers
        finger_count = 0
        fingertips = []
        
        # Get bounding box for reference
        x, y, w, h = cv2.boundingRect(contour)
        
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(contour[s][0])
            end = tuple(contour[e][0])
            far = tuple(contour[f][0])
            
            # Calculate triangle sides
            a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            
            # Calculate angle
            try:
                angle = np.arccos((b**2 + c**2 - a**2) / (2*b*c)) * 180 / np.pi
            except:
                continue
                
            # Filter defects by angle and position
            if angle <= 90 and d/256.0 > 10:
                # This is likely a finger valley
                # Mark the defect point
                cv2.circle(output, far, 5, [255, 0, 0], -1)
                fingertips.append(end)
                finger_count += 1
                
        # Add 1 for the hand itself
        finger_count = min(finger_count + 1, 5)
        
        # Draw fingertips
        for tip in fingertips:
            cv2.circle(output, tip, 8, [0, 255, 255], -1)
            
        # Add label for finger count
        cv2.putText(output, f'Fingers: {finger_count}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
        return output, finger_count
        
    def process_image(self, img):
        """Process image and count fingers"""
        # Convert BGR to RGB if needed
        if img.shape[2] == 3 and np.mean(img[:,:,0]) > np.mean(img[:,:,2]):
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Detect skin
        skin_mask = self.detect_skin(img)
        
        # Get hand contour
        hand_contour = self.get_hand_contour(skin_mask)
        
        # Count fingers (without thumb detection)
        result_img, fingers = self.count_fingers(hand_contour, img)
        
        # Add debug view of skin mask
        mask_small = cv2.resize(skin_mask, (result_img.shape[1]//4, result_img.shape[0]//4))
        mask_color = cv2.cvtColor(mask_small, cv2.COLOR_GRAY2BGR)
        
        # Place mask in corner for debugging
        result_img[0:mask_color.shape[0], 0:mask_color.shape[1]] = mask_color
        
        return result_img, fingers

# Create a single global instance of the detector
detector = SimpleHandDetector()

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
    
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image from {image_path}")
    
    # Process image using the new detector
    result_img, fingers = detector.process_image(image)
    
    # Update global variables for other functions to use
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
    # Use the new detector to process the image
    finger_count = detect_fingers(image_path)
    
    # Return the count and the visualization
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
    # Use detect_fingers to process the image and update the hand_skeleton_image
    finger_count = detect_fingers(image_path)
    
    # Check if we have a valid skeleton image
    if hand_skeleton_image is not None:
        # Save the debug image
        cv2.imwrite(output_path, hand_skeleton_image)
    else:
        # Create a basic debug image if hand_skeleton_image is not available
        image = cv2.imread(image_path)
        if image is not None:
            cv2.putText(image, f"No hand detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imwrite(output_path, image)