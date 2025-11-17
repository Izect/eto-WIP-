import os
import sys
import cv2
from ultralytics import YOLO

model_path = 'yolo11s_candy_model.pt'
min_thresh = 0.50
cam_index = 0
imgW, imgH = 1280, 720
record = False

nutrition_info = nutrition_info = {
    'Bar_One': [201, 21],
    'Gems': [50, 9],
    'Kit_Kat': [106, 11],
    'Milky_Bar': [137, 14]
}


if (not os.path.exists(model_path)):
    print('WARNING: Model path is invalid or model was not found.')
    sys.exit()

model = YOLO(model_path, task='detect')
labels = model.names

cap = cv2.VideoCapture(cam_index)
ret = cap.set(3, imgW)
ret = cap.set(4, imgH)

if record == True:
    record_name = 'demo1.avi'
    record_fps = 30
    recorder = cv2.VideoWriter(record_name, cv2.VideoWriter_fourcc(*'MJPG'), record_fps, (imgW,imgH))

bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
              (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]

while True:
    ret, frame = cap.read()
    if (frame is None) or (not ret):
        print('Unable to read frames from the camera. This indicates the camera is disconnected or not working. Exiting program.')
        break

    results = model.track(frame, verbose=False)
    detections = results[0].boxes
    candies_detected = []

    for i in range(len(detections)):
        xyxy_tensor = detections[i].xyxy.cpu()
        xyxy = xyxy_tensor.numpy().squeeze()
        xmin, ymin, xmax, ymax = xyxy.astype(int)

        classidx = int(detections[i].cls.item())
        classname = labels[classidx]

        conf = detections[i].conf.item()

        if conf > 0.5:
            color = bbox_colors[classidx % 10]
            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), color, 2)
            label = f'{classname}: {int(conf*100)}%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            label_ymin = max(ymin, labelSize[1] + 10)
            cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), color, cv2.FILLED)
            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            candies_detected.append(classname)
    
    total_calories = 0
    total_sugar = 0

    for candy_name in candies_detected:
        calories, sugar = nutrition_info[candy_name]
        total_calories += calories
        total_sugar += sugar

    cv2.rectangle(frame, (10, 10), (450, 130), (50,50,50), cv2.FILLED)
    cv2.putText(frame, f'Number of candies: {len(candies_detected)}', (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,102,51), 2)
    cv2.putText(frame, f'Total calories: {total_calories}', (20,75), cv2.FONT_HERSHEY_SIMPLEX, 1, (51,204,51), 2)
    cv2.putText(frame, f'Total sugar (g): {total_sugar}', (20,110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,204,255), 2)

    cv2.imshow('Candy detection results',frame)
    if record: recorder.write(frame)

    key = cv2.waitKey(5)
    if key == ord('q') or key == ord('Q'):
        break
    elif key == ord('s') or key == ord('S'):
        cv2.waitKey()
    elif key == ord('p') or key == ord('P'):
        cv2.imwrite('capture.png',frame)

cap.release()
if record: recorder.release()
cv2.destroyAllWindows()