import argparse
import glob
import os
import sys
import time
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO  # type:ignore

COLORS = {
    "green": (0, 255, 0),
    "blue": (255, 0, 0),
    "yellow": (0, 255, 255),
    "orange": (0, 165, 255),
    "red": (0, 0, 255),
}

parser = argparse.ArgumentParser()
parser.add_argument(
    "--model",
    help='Path to YOLO model file (example: "runs/detect/train/weights/best.pt")',
    required=True,
)
parser.add_argument(
    "--source",
    help='Image source, can be image file ("test.jpg"), image folder ("test_dir"), video file ("testvid.mp4"), index of USB camera ("usb0"), or index of Picamera ("picamera0")',
    required=True,
)
parser.add_argument(
    "--thresh",
    help='Minimum confidence threshold for displaying detected objects (example: "0.4")',
    default=0.5,
)
parser.add_argument(
    "--resolution",
    help='Resolution in WxH to display inference results at (example: "640x480"), otherwise, match source resolution',
    default=None,
)
parser.add_argument(
    "--record",
    help='Record results from video or webcam and save it as "demo1.avi". Must specify --resolution argument to record.',
    action="store_true",
)

args = parser.parse_args()

nutrition_info = {
    "Bar_One": [201, 21],
    "Gems": [50, 9],
    "Kit-Kat": [106, 11],
    "Milky_Bar": [137, 14],
}

model_path = args.model
img_source = args.source
min_thresh = float(args.thresh)
user_res = args.resolution
record = args.record

if not os.path.exists(model_path):
    print(
        "ERROR: Model path is invalid or model was not found. Make sure the model filename was entered correctly."
    )
    sys.exit(0)

model = YOLO(model_path, task="detect")
labels = model.names

print("Detected YOLO classes:", labels)

img_ext_list = [".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG", ".bmp", ".BMP"]
vid_ext_list = [".avi", ".mov", ".mp4", ".mkv", ".wmv"]

if os.path.isdir(img_source):
    source_type = "folder"
elif os.path.isfile(img_source):
    _, ext = os.path.splitext(img_source)
    if ext in img_ext_list:
        source_type = "image"
    elif ext in vid_ext_list:
        source_type = "video"
    else:
        print(f"File extension {ext} is not supported.")
        sys.exit(0)
elif "usb" in img_source:
    source_type = "usb"
    usb_idx = int(img_source[3:])
elif "picamera" in img_source:
    source_type = "picamera"
    picam_idx = int(img_source[8:])
else:
    print(f"Input {img_source} is invalid. Please try again.")
    sys.exit(0)

resize = False
if user_res:
    try:
        parts = user_res.split("x")
        if len(parts) != 2:
            raise ValueError
        resW, resH = int(parts[0]), int(parts[1])
        resize = True
    except (ValueError, IndexError):
        print("ERROR: Resolution must be in format WxH (e.g., 640x480).")
        sys.exit(0)

if record:
    if source_type not in ["video", "usb"]:
        print("Recording only works for video and camera sources. Please try again.")
        sys.exit(0)
    if not user_res:
        print("Please specify resolution to record video at.")
        sys.exit(0)
    record_name = "demo1.avi"
    record_fps = 30
    recorder = cv2.VideoWriter(
        record_name,
        cv2.VideoWriter_fourcc(*"MJPG"),  # type:ignore
        record_fps,
        (resW, resH),  # type:ignore
    )

if source_type == "image":
    imgs_list = [img_source]
elif source_type == "folder":
    imgs_list = []
    filelist = glob.glob(img_source + "/*")
    for file in filelist:
        _, file_ext = os.path.splitext(file)
        if file_ext in img_ext_list:
            imgs_list.append(file)
elif source_type == "video" or source_type == "usb":
    if source_type == "video":
        cap_arg = img_source
    elif source_type == "usb":
        cap_arg = usb_idx
    cap = cv2.VideoCapture(cap_arg)
    if user_res:
        ret = cap.set(3, resW)
        ret = cap.set(4, resH)
elif source_type == "picamera":
    from picamera2 import Picamera2

    if not user_res:
        resW, resH = 640, 480

    cap = Picamera2()
    cap.configure(
        cap.create_video_configuration(main={"format": "RGB888", "size": (resW, resH)})
    )
    cap.start()

bbox_colors = [
    (164, 120, 87),
    (68, 148, 228),
    (93, 97, 209),
    (178, 182, 133),
    (88, 159, 106),
    (96, 202, 231),
    (159, 124, 168),
    (169, 162, 241),
    (98, 118, 150),
    (172, 176, 184),
]

avg_frame_rate = 0
frame_rate_buffer = []
fps_avg_len = 200
img_count = 0
show_info = True


def classify_sweets_calories(total_calories: float) -> tuple:
    if total_calories <= 100:
        return ("Safe", COLORS["green"])
    elif total_calories <= 200:
        return ("Moderate", COLORS["blue"])
    elif total_calories <= 400:
        return ("High", COLORS["yellow"])
    elif total_calories <= 700:
        return ("Excessive", COLORS["orange"])
    else:
        return ("Extreme", COLORS["red"])


def display_risk_level(
    frame,
    risk_level: tuple,
    position: tuple = (20, 300),
    font: int = cv2.FONT_HERSHEY_SIMPLEX,
    font_scale: float = 1,
    thickness: int = 2,
):
    label, color = risk_level
    text = f"Risk Level: {label}"

    cv2.putText(
        frame,
        text,
        position,
        font,
        font_scale,
        (0, 0, 0),
        thickness + 3,
        lineType=cv2.LINE_AA,
    )

    cv2.putText(
        frame, text, position, font, font_scale, color, thickness, lineType=cv2.LINE_AA
    )

    return frame


while True:
    t_start = time.perf_counter()

    if source_type == "image" or source_type == "folder":
        if img_count >= len(imgs_list):
            print("All images have been processed. Exiting program.")
            sys.exit(0)
        img_filename = imgs_list[img_count]
        frame: Any = cv2.imread(img_filename)
        img_count = img_count + 1
    elif source_type == "video":
        ret, frame = cap.read()
        if not ret:
            print("Reached end of the video file. Exiting program.")
            break
    elif source_type == "usb":
        ret, frame = cap.read()
        if (frame is None) or (not ret):
            print("Camera error. Exiting.")
            break
    elif source_type == "picamera":
        frame = cap.capture_array()  # type:ignore
        if frame is None:
            print("Camera error. Exiting.")
            break

    if resize:
        frame = cv2.resize(frame, (resW, resH))  # type:ignore

    results = model(frame, verbose=False)

    candies_detected = []
    candy_counts = {name: 0 for name in nutrition_info}

    for box in results[0].boxes:
        xmin, ymin, xmax, ymax = box.xyxy[0].cpu().numpy().astype(int)

        classidx = int(box.cls.item())
        classname = labels[classidx]
        conf = box.conf[0].item()

        if conf > min_thresh:
            color = bbox_colors[classidx % 10]
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
            label = f"{classname}: {int(conf * 100)}%"
            labelSize, baseLine = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            label_ymin = max(ymin, labelSize[1] + 10)
            cv2.rectangle(
                frame,
                (xmin, label_ymin - labelSize[1] - 10),
                (xmin + labelSize[0], label_ymin + baseLine - 10),
                color,
                cv2.FILLED,
            )
            cv2.putText(
                frame,
                label,
                (xmin, label_ymin - 7),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
            )
            candies_detected.append(classname)
            if classname in candy_counts:
                candy_counts[classname] += 1

    total_calories = sum(nutrition_info[c][0] * n for c, n in candy_counts.items())
    total_sugar = sum(nutrition_info[c][1] * n for c, n in candy_counts.items())
    risk_level = classify_sweets_calories(total_calories)

    if show_info:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        padding = 20

        texts_to_measure = [
            f"Number of candies: {sum(candy_counts.values())}",
            f"Total calories: {total_calories}",
            f"Total sugar (g): {total_sugar}",
            f"Risk Level: {risk_level[0]}",
        ]
        if source_type in ["video", "usb", "picamera"]:
            texts_to_measure.append(f"FPS: {avg_frame_rate:0.2f}")

        for candy, count in candy_counts.items():
            texts_to_measure.append(f"{candy}: {count}")

        max_text_width = 0
        for text in texts_to_measure:
            if text.startswith("Risk"):
                (w, h), _ = cv2.getTextSize(text, font, font_scale * 2, thickness * 2)
            else:
                (w, h), _ = cv2.getTextSize(text, font, font_scale, thickness)
            max_text_width = max(max_text_width, w)

        if len(candy_counts) > 0:
            final_y_pos = 200 + ((len(candy_counts) - 1) * 32) + 15
        else:
            final_y_pos = 130

        box_x2 = 10 + max_text_width + padding
        box_y2 = final_y_pos + padding

        cv2.rectangle(frame, (10, 10), (box_x2, box_y2), (50, 50, 50), cv2.FILLED)

        cv2.putText(
            frame,
            f"Number of candies: {sum(candy_counts.values())}",
            (20, 40),
            font,
            font_scale,
            (255, 102, 51),
            thickness,
        )
        cv2.putText(
            frame,
            f"Total calories: {total_calories}",
            (20, 75),
            font,
            font_scale,
            (51, 204, 51),
            thickness,
        )
        cv2.putText(
            frame,
            f"Total sugar (g): {total_sugar}",
            (20, 110),
            font,
            font_scale,
            (0, 204, 255),
            thickness,
        )

        y_start = 150
        for idx, (candy, count) in enumerate(candy_counts.items()):
            cv2.putText(
                frame,
                f"{candy}: {count}",
                (20, y_start + idx * 32),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
            )

        display_risk_level(frame, risk_level)

        if source_type in ["video", "usb", "picamera"]:
            cv2.putText(
                frame,
                f"FPS: {avg_frame_rate:0.2f}",
                (10, 20),
                font,
                font_scale,
                (0, 255, 255),
                thickness,
            )

    cv2.imshow("YOLO Candy Calorie Counter", frame)
    if record:
        recorder.write(frame)

    t_stop = time.perf_counter()
    frame_rate_calc = float(1 / (t_stop - t_start)) if (t_stop - t_start) > 0 else 0.0

    if len(frame_rate_buffer) >= fps_avg_len:
        temp = frame_rate_buffer.pop(0)
        frame_rate_buffer.append(frame_rate_calc)
    else:
        frame_rate_buffer.append(frame_rate_calc)
    avg_frame_rate = np.mean(frame_rate_buffer)

    if source_type in ["image", "folder"]:
        key = cv2.waitKey(0)
    else:
        key = cv2.waitKey(5)

    if key == ord("q") or key == ord("Q"):
        break
    elif key == ord("s") or key == ord("S"):
        if source_type in ["image", "folder"]:
            img_count = max(0, img_count - 2)
        cv2.waitKey(1)
    elif key == ord("p") or key == ord("P"):
        cv2.imwrite("capture.png", frame)
        if source_type in ["image", "folder"]:
            img_count -= 1
    elif key == ord("t") or key == ord("T"):
        show_info = not show_info
        if source_type in ["image", "folder"]:
            img_count -= 1


print(f"Average pipeline FPS: {avg_frame_rate:.2f}")
if source_type in ["video", "usb"]:
    cap.release()
elif source_type == "picamera":
    cap.stop()  # type:ignore
if record:
    recorder.release()
cv2.destroyAllWindows()
