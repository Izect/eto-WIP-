# YOLO Sweet Calorie Counter & Risk Detector

This application uses computer vision (YOLOv8) to detect specific brands of sweets/candies in real-time. It counts the detected items, calculates the total caloric and sugar intake, and assesses the health "Risk Level" based on the total calories.

## 📋 Features
* **Object Detection:** Identifies `Bar_One`, `Gems`, `Kit-Kat`, and `Milky_Bar`.
* **Calorie & Sugar Calculation:** sums up nutritional values based on detected quantities.
* **Risk Assessment:** Classifies the total calorie count into risk levels (Safe to Extreme).
* **Multi-Source Support:** Works with Images, Videos, Image Folders, USB Webcams, and Raspberry Pi Cameras (Picamera2).
* **Recording:** Option to record live inference to a video file.

---

## ⚙️ Installation

1.  **Clone the repository** (or download the script).
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If using a Raspberry Pi Camera, ensure `picamera2` is installed on your system.*

---

## 🚀 Usage

Run the script from the command line using `python yolo_detect.py` followed by the required arguments.

### Common Commands

**1. Run on a single image:**
```bash
python yolo_detect.py --model "my_model (1)/train3/weights/best.pt" --source images/test.jpg
````

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

-----

### 🎛️ Command Line Arguments

| Argument | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `--model` | **Yes** | Path to your trained YOLO `.pt` file. | `--model best.pt` |
| `--source` | **Yes** | Input source (file path, folder, `usb0`, or `picamera0`). | `--source usb0` |
| `--thresh` | No | Confidence threshold for detection (Default: 0.5). | `--thresh 0.6` |
| `--resolution`| No | Force display resolution (WxH). | `--resolution 640x480` |
| `--record` | No | Record output to `demo1.avi` (Requires `--resolution`). | `--record` |

### Recording Example

To record a webcam stream, you **must** specify the resolution:

```bash
python yolo_detect.py --model best.pt --source usb0 --resolution 640x480 --record
```

-----

## ⌨️ Keyboard Controls

While the window is active, you can use the following keys to control the application:

| Key | Function |
| :---: | :--- |
| **Q** | **Quit** the application. |
| **P** | **Screenshot**: Saves the current frame as `capture.png`. |
| **T** | **Toggle Info**: Hides/Shows the nutrition overlay box. |
| **S** | **Previous Image**: Go back one image (only works in Image/Folder mode). |

-----

## 📊 Risk Levels

The application classifies the total calories on screen into the following categories:

| Total Calories | Risk Level | Color Indicator |
| :--- | :--- | :--- |
| 0 - 100 | **Safe** | 🟢 Green |
| 101 - 200 | **Moderate** | 🔵 Blue |
| 201 - 400 | **High** | 🟡 Yellow |
| 401 - 700 | **Excessive** | 🟠 Orange |
| 700+ | **Extreme** | 🔴 Red |
