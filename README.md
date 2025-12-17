# YOLO Sweet Calorie Counter & Risk Detector

This application uses computer vision (YOLOv8) to detect specific brands of sweets/candies in real-time. It counts the detected items, calculates the total caloric and sugar intake, and assesses the health "Risk Level" based on the total calories.

Available in two modes:
- **Desktop Application** - Python script with OpenCV interface
- **Web Application** - Browser-based interface with live video analysis

---

## 📋 Features

* **Object Detection:** Identifies `Bar_One`, `Gems`, `Kit-Kat`, and `Milky_Bar`.
* **Calorie & Sugar Calculation:** Sums up nutritional values based on detected quantities.
* **Risk Assessment:** Classifies the total calorie count into risk levels (Safe to Extreme).
* **Bounding Box Visualization:** Visual detection with labeled boxes and confidence scores.
* **Multi-Source Support:** 
  - Desktop: Images, Videos, Image Folders, USB Webcams, and Raspberry Pi Cameras
  - Web: Image upload, camera capture, and live video analysis
* **Recording:** Option to record live inference to a video file (desktop only).

---

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Izect/eto-WIP-.git
   cd eto-WIP-
   ```

2. **Install dependencies:**
   ```bash
   git lfs install
   git lfs pull
   pip install -r requirements.txt
   ```
   *Note: If using a Raspberry Pi Camera, ensure `picamera2` is installed on your system.*

---

## 🚀 Usage

### Desktop Application

Run the script from the command line using `python yolo_detect.py` followed by the required arguments.

#### Common Commands

**1. Run on a single image:**
```bash
python yolo_detect.py --model "my_model (1)/train3/weights/best.pt" --source images/test.jpg
```

**2. Run on a video file:**
```bash
python yolo_detect.py --model "my_model (1)/train3/weights/best.pt" --source videos/demo.mp4
```

**3. Run on a USB Webcam (Index 0):**
```bash
python yolo_detect.py --model "my_model (1)/train3/weights/best.pt" --source usb0
```

**4. Run on a specific folder of images:**
```bash
python yolo_detect.py --model "my_model (1)/train3/weights/best.pt" --source ./my_test_images/
```

**5. Run using Raspberry Pi Camera:**
```bash
python yolo_detect.py --model "my_model (1)/train3/weights/best.pt" --source picamera0
```

#### 🎛️ Command Line Arguments

| Argument | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `--model` | **Yes** | Path to your trained YOLO `.pt` file. | `--model best.pt` |
| `--source` | **Yes** | Input source (file path, folder, `usb0`, or `picamera0`). | `--source usb0` |
| `--thresh` | No | Confidence threshold for detection (Default: 0.5). | `--thresh 0.6` |
| `--resolution`| No | Force display resolution (WxH). | `--resolution 640x480` |
| `--record` | No | Record output to `demo1.avi` (Requires `--resolution`). | `--record` |

#### Recording Example
To record a webcam stream, you **must** specify the resolution:
```bash
python yolo_detect.py --model best.pt --source usb0 --resolution 640x480 --record
```

#### ⌨️ Keyboard Controls

While the window is active, you can use the following keys to control the application:

| Key | Function |
| :---: | :--- |
| **Q** | **Quit** the application. |
| **P** | **Screenshot**: Saves the current frame as `capture.png`. |
| **T** | **Toggle Info**: Hides/Shows the nutrition overlay box. |
| **S** | **Previous Image**: Go back one image (only works in Image/Folder mode). |

---

### Web Application

The web application provides an intuitive browser-based interface with three detection modes.

#### 🌐 Starting the Web Application

1. **Start the Python server:**
   ```bash
   python server.py
   ```
   This will start the API server on `http://localhost:8000`

2. **Open the web interface:**
   - Open `index.html` in your web browser

#### 🎯 Detection Modes

1. **📤 Upload Image**
   - Click to browse or drag and drop an image
   - Supports PNG, JPG, and JPEG formats
   - View results with bounding boxes

2. **📷 Capture Photo**
   - Take a single snapshot using your device camera
   - Analyze the captured image
   - Perfect for quick scans

3. **🎥 Live Video Analysis**
   - Real-time continuous detection
   - Analyzes frames every 0.5 seconds
   - Shows FPS counter
   - Live bounding box overlay on video stream

#### 🖱️ Web Interface Controls

- **Analyze Image** - Process uploaded/captured image
- **Go Back** - Return to upload screen
- **Stop Live Analysis** - End live video session
- **Cancel** - Exit camera/video mode

#### 📊 Results Display

The web interface shows:
- Total number of candies detected
- Total calories and sugar content
- Color-coded risk level indicator
- Detailed breakdown per candy type
- Visual bounding boxes with confidence scores

---

## 📊 Risk Levels

The application classifies the total calories on screen into the following categories:

| Total Calories | Risk Level | Color Indicator |
| :--- | :--- | :--- |
| 0 - 100 | **Safe** | 🟢 Green |
| 101 - 200 | **Moderate** | 🔵 Blue |
| 201 - 400 | **High** | 🟡 Yellow |
| 401 - 700 | **Excessive** | 🟠 Orange |
| 700+ | **Extreme** | 🔴 Red |

---

## 🔧 Configuration

### Model Path
Update the model path in both applications:
- **Desktop:** `--model` argument
- **Web:** Edit `MODEL_PATH` in `server.py`

### Confidence Threshold
Adjust detection sensitivity:
- **Desktop:** `--thresh` argument
- **Web:** Edit `MIN_THRESH` in `server.py`

### Nutrition Values
Modify candy nutritional information in:
- **Desktop:** `nutrition_info` dictionary in `yolo_detect.py`
- **Web:** `NUTRITION_INFO` in `server.py` and `index.html`

---

## 🐛 Troubleshooting

### Desktop Application
- **Camera not found:** Check USB index or Picamera connection
- **Model not loading:** Verify path to `.pt` file
- **Low FPS:** Reduce resolution or adjust confidence threshold
- **Inaccurate detections:** Check image quality and lighting conditions

### Web Application
- **Camera access denied:** Allow camera permissions in browser
- **Server connection failed:** Ensure `server.py` is running on port 8000
- **Inaccurate detections:** Check image quality and lighting conditions

---

## 📝 Notes

- The web application requires the Python server to be running for inference
- For best results, ensure good lighting and clear view of candies
- Live video analysis has a half-second interval to balance accuracy and performance

---
