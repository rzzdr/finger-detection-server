# Finger Detection Server for ESP32-CAM

A Python FastAPI server that processes images to detect fingers using computer vision techniques. This server can work with ESP32-CAM to control LEDs via a relay module based on the number of fingers detected.

## Project Overview

This project consists of:
1. A FastAPI server that processes images and detects fingers using OpenCV
2. Integration with ESP32-CAM for image capture and relay control
3. Image processing logic to detect and count fingers (0-4)
4. Real-time visualization of the finger detection process

## Requirements

- Python 3.8 or higher
- Dependencies can be installed via Poetry or pip (requirements.txt provided)
- For testing: Webcam connected to your computer
- For practical application: ESP32-CAM module and 4-channel relay module

## Installation

### Option 1: Using Poetry (Recommended)

1. Clone this repository
2. Install Poetry if you don't have it:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   or on Windows:
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

3. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

### Option 2: Using pip

1. Clone this repository
2. Install dependencies with pip:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

### Using Poetry:

```bash
poetry run python main.py
```

### Using regular Python:

```bash
python main.py
```

The server will start on `http://0.0.0.0:8000`
API documentation available at `http://0.0.0.0:8000/docs`

## Project Structure

## API Endpoints

### POST /upload

Accepts an image and returns the number of fingers detected.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image)

**Response:**
```json
{
  "fingers": 3
}
```

### GET /status

A simple health check endpoint.

**Response:**
```json
{
  "status": "online"
}
```

## ESP32-CAM Integration

For the ESP32-CAM side, you'll need to:

1. Capture an image
2. Send it to the FastAPI server
3. Parse the response to get the finger count
4. Control the relay module based on the finger count

Example Arduino code for the ESP32-CAM:

```cpp
#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server address (replace with your server's IP address and port)
const char* serverUrl = "http://192.168.1.100:8000/upload";

// Relay pins - adjust according to your setup
const int relayPins[] = {12, 13, 14, 15};  // Example GPIO pins
const int numRelays = 4;

void setup() {
  Serial.begin(115200);
  
  // Initialize relay pins
  for (int i = 0; i < numRelays; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], LOW);  // Relays off initially
  }
  
  // Initialize WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
  
  // Initialize camera (add your camera configuration here)
  // ...
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // Take a photo
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }
    
    // Send the image to the server
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");
    
    // Send the request
    int httpResponseCode = http.POST(fb->buf, fb->len);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      
      // Parse the response to get the finger count
      DynamicJsonDocument doc(1024);
      deserializeJson(doc, response);
      int fingerCount = doc["fingers"];
      
      Serial.print("Fingers detected: ");
      Serial.println(fingerCount);
      
      // Control relays based on finger count
      controlRelays(fingerCount);
    }
    else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
    esp_camera_fb_return(fb);
  }
  
  // Wait before next capture
  delay(5000);
}

void controlRelays(int count) {
  // Turn all relays off first
  for (int i = 0; i < numRelays; i++) {
    digitalWrite(relayPins[i], LOW);
  }
  
  // Turn on the relays based on finger count
  for (int i = 0; i < count && i < numRelays; i++) {
    digitalWrite(relayPins[i], HIGH);
  }
}
```

## How the Finger Detection Works

The finger detection algorithm uses computer vision techniques and mathematical principles to detect and count fingers in an image. Here's a detailed explanation of how it works:

### 1. Color Space Conversion and Skin Detection
The algorithm first converts RGB images to HSV (Hue-Saturation-Value) color space, which separates color information (hue) from intensity (value) and saturation, making it more robust for skin detection under varying lighting conditions.

#### Mathematical basis:
For each pixel RGB(r,g,b), the conversion to HSV follows:
```
V = max(r,g,b)
S = (V-min(r,g,b))/V if V≠0, otherwise S=0
H = {
    60° × (g-b)/(V-min(r,g,b)) if V=r
    60° × (2+(b-r)/(V-min(r,g,b))) if V=g
    60° × (4+(r-g)/(V-min(r,g,b))) if V=b
}
```

#### Skin Detection Parameters:
Two HSV ranges are used to accommodate various skin tones:
- Primary range: H[0-20], S[20-255], V[70-255]
- Secondary range: H[170-180], S[20-255], V[70-255]

The ranges are combined using a bitwise OR operation to create a binary mask where white pixels (255) represent skin.

### 2. Mask Enhancement
The binary mask is enhanced through morphological operations:
- **Dilation**: Expands white regions using kernel K: `Dilate(I) = I ⊕ K`
- **Erosion**: Shrinks white regions using kernel K: `Erode(I) = I ⊖ K`
- **Gaussian Blur**: Applied with kernel size (5,5) to smooth edges:
  ```
  G(x,y) = (1/(2πσ²)) * e^(-(x²+y²)/(2σ²))
  ```

### 3. Contour Extraction
The algorithm finds contours in the binary mask using border following algorithm. The largest contour is selected as the hand, filtering out contours with area < 5000 pixels to eliminate noise.

### 4. Convex Hull and Defects Analysis
The convex hull is a convex polygon that encloses the hand contour. Mathematically, for points P in the contour, the convex hull H is:
```
H = {∑(λᵢpᵢ) | pᵢ ∈ P, λᵢ ≥ 0, ∑λᵢ = 1}
```

**Convexity defects** are regions where the contour deviates from the hull - these represent spaces between fingers.

Each defect is defined by four points:
- Start point (s): Point on the hull
- End point (e): Next point on the hull
- Far point (f): Farthest point on the contour from the line segment between start and end
- Distance (d): Distance from far point to the hull

### 5. Mathematical Angle Calculation for Finger Identification
For each defect, the algorithm forms a triangle between start(s), end(e), and far(f) points.

The sides of the triangle are:
```
a = √((eₓ - sₓ)² + (eᵧ - sᵧ)²)
b = √((fₓ - sₓ)² + (fᵧ - sᵧ)²)
c = √((eₓ - fₓ)² + (eᵧ - fᵧ)²)
```

Using the Law of Cosines, the angle (θ) at the far point is calculated:
```
θ = arccos((b² + c² - a²)/(2bc)) × (180/π)
```

Finger valleys are identified when:
1. θ ≤ 90° (acute angle between fingers)
2. d/256 > 10 (sufficient depth of defect)

### 6. Final Finger Count
The number of identified defects plus one gives the finger count (accounting for the thumb or last finger). The maximum is capped at 4 fingers.

### Advanced Visualization
The algorithm draws:
- Hand contours in green
- Convexity defect points in red
- Fingertips in yellow
- A small thumbnail of the skin mask in the corner for debugging

### Parameters Tuning
Key parameters that may require adjustment based on lighting and skin tone include:
- HSV ranges for skin detection (in `detect_skin` method)
- Minimum contour area threshold (currently 5000 pixels)
- Angle threshold (currently 90°)
- Defect depth threshold (currently d/256 > 10)

## Troubleshooting

- If the finger detection is not accurate, try adjusting the HSV color range in `app/core/finger_detection.py`
- For debugging, use the `save_debug_image` function in `app/core/finger_detection.py`
- Ensure the ESP32-CAM has good lighting conditions for better detection

## License

MIT
