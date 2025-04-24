import cv2
import requests
import os
import time
from io import BytesIO

# Configuration
API_URL = "http://localhost:8000/upload"
CAPTURE_DELAY = 1
WINDOW_NAME = "Finger Counter - Press 'q' to quit"

def capture_and_detect():
    """
    Captures images from the webcam and sends them to the finger detection API.
    Displays the webcam feed and finger count in real-time.
    """
    # Initialize webcam
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Webcam initialized. Press 'q' to quit.")
    
    last_capture_time = 0
    
    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                print("Error: Failed to capture image")
                break
            
            frame = cv2.flip(frame, 1)
            
            current_time = time.time()
            time_since_last = current_time - last_capture_time
            if time_since_last < CAPTURE_DELAY:
                countdown = CAPTURE_DELAY - time_since_last
                cv2.putText(frame, f"Next capture in: {countdown:.1f}s", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "Capturing...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if time_since_last >= CAPTURE_DELAY:
                    fingers = process_frame(frame)
                    last_capture_time = current_time
                    
                    if fingers is not None:
                        cv2.putText(frame, f"Fingers detected: {fingers}", 
                                  (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.9, (255, 0, 0), 2)
            
            cv2.imshow(WINDOW_NAME, frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cam.release()
        cv2.destroyAllWindows()
        print("Camera released and application closed.")

def process_frame(frame):
    """
    Sends a frame to the finger detection API and returns the finger count
    
    Args:
        frame: Image captured from webcam
        
    Returns:
        int: Number of fingers detected or None if there was an error
    """
    try:
        _, img_encoded = cv2.imencode('.jpg', frame)
        
        files = {'image': ('image.jpg', BytesIO(img_encoded.tobytes()), 'image/jpeg')}
        
        print("Sending image to API...")
        response = requests.post(
            API_URL, 
            files=files,
            params={
                'min_finger_length': 30, 
                'min_angle': 80,
                'use_skeleton': True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            fingers = result.get('fingers', 0)
            print(f"Number of fingers detected: {fingers}")
            return fingers
        else:
            print(f"API error: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        print(f"Error processing frame: {str(e)}")
        return None

if __name__ == "__main__":
    print("Starting webcam finger counter...")
    print(f"Connecting to API at {API_URL}")
    print("Make sure the finger detection server is running!")
    
    # Check if server is running before starting
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("Server connection successful.")
            capture_and_detect()
        else:
            print(f"Server returned unexpected response: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Please make sure the finger detection server is running.")
        print("You can start it by running: python main.py")