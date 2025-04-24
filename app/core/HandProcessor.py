import cv2
import numpy as np

# Global variable to store the most recent finger count
last_detected_count = 0
hand_skeleton_image = None

class HandProcessor:
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
            
        output = img.copy()
        
        cv2.drawContours(output, [contour], -1, (0, 255, 0), 2)
        
        hull = cv2.convexHull(contour, returnPoints=False)
        
        try:
            defects = cv2.convexityDefects(contour, hull)
        except:
            return output, 0
            
        if defects is None:
            return output, 0
            
        finger_count = 0
        fingertips = []
        
        x, y, w, h = cv2.boundingRect(contour)
        
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(contour[s][0])
            end = tuple(contour[e][0])
            far = tuple(contour[f][0])
            
            a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            
            try:
                angle = np.arccos((b**2 + c**2 - a**2) / (2*b*c)) * 180 / np.pi
            except:
                continue
                
            if angle <= 90 and d/256.0 > 10:
                cv2.circle(output, far, 5, [255, 0, 0], -1)
                fingertips.append(end)
                finger_count += 1
                
        finger_count = min(finger_count + 1, 5)
        
        for tip in fingertips:
            cv2.circle(output, tip, 8, [0, 255, 255], -1)
            
        cv2.putText(output, f'Fingers: {finger_count}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
        return output, finger_count
        
    def process_image(self, img):
        """Process image and count fingers"""
        if img.shape[2] == 3 and np.mean(img[:,:,0]) > np.mean(img[:,:,2]):
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Detect skin
        skin_mask = self.detect_skin(img)
        
        # Get hand contour
        hand_contour = self.get_hand_contour(skin_mask)
        
        # Count fingers
        result_img, fingers = self.count_fingers(hand_contour, img)
        
        # skin mask
        mask_small = cv2.resize(skin_mask, (result_img.shape[1]//4, result_img.shape[0]//4))
        mask_color = cv2.cvtColor(mask_small, cv2.COLOR_GRAY2BGR)
        
        # Place mask in corner for debugging
        result_img[0:mask_color.shape[0], 0:mask_color.shape[1]] = mask_color
        
        return result_img, fingers