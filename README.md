# Finger Detection Server for ESP32-CAM

A Python FastAPI server that works with an ESP32-CAM to detect the number of fingers in an image and control LEDs via a relay module.

## Project Overview

This project consists of:
1. A FastAPI server that processes images and detects fingers using OpenCV
2. Integration with ESP32-CAM for image capture and relay control
3. Image processing logic to detect and count fingers (1-4)

## Requirements

- Python 3.8 or higher
- Poetry for dependency management
- ESP32-CAM module
- 4-channel relay module
- 4 LEDs

## Installation

1. Clone this repository
2. Install dependencies with Poetry:

```bash
poetry install
```

## Running the Server

```bash
poetry run python main.py
```

The server will start on `http://0.0.0.0:8000`

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

The finger detection algorithm:

1. Converts the image to HSV color space
2. Detects skin color using predefined HSV ranges
3. Creates a binary mask of the hand
4. Finds contours in the mask
5. Calculates convex hull and convexity defects
6. Counts fingers based on angles between defects

You may need to adjust the skin detection parameters based on your lighting conditions.

## Troubleshooting

- If the finger detection is not accurate, try adjusting the HSV color range in `app/core/finger_detection.py`
- For debugging, use the `save_debug_image` function in `app/core/finger_detection.py`
- Ensure the ESP32-CAM has good lighting conditions for better detection

## License

MIT