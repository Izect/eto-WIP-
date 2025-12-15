import base64
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

import cv2
import numpy as np
from ultralytics import YOLO  # type:ignore

MODEL_PATH = "my_model (1)/train3/weights/best.pt"
model = YOLO(MODEL_PATH, task="detect")

MIN_THRESH = 0.5


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_POST(self):
        if self.path.rstrip("/") == "/api/send":
            try:
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                image_data = data.get("image_data")
                image_bytes = base64.b64decode(image_data)

                nparr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                results = model(frame, verbose=False)  # type:ignore

                detections = []
                for box in results[0].boxes:
                    xmin, ymin, xmax, ymax = (
                        box.xyxy[0].cpu().numpy().astype(int).tolist()
                    )
                    classidx = int(box.cls.item())
                    classname = model.names[classidx]
                    conf = box.conf[0].item()

                    print(
                        f"Detection: {classname} @ {conf:.3f} | bbox: [{xmin}, {ymin}, {xmax}, {ymax}]"
                    )

                    if conf > MIN_THRESH:
                        detections.append(
                            {
                                "candy": classname,
                                "confidence": round(conf, 3),
                                "bbox": [xmin, ymin, xmax, ymax],
                            }
                        )

                print(
                    f"Detected {len(detections)} candies above threshold {MIN_THRESH}"
                )
                print("-" * 50)

                self._set_headers()
                response = {
                    "content": [
                        {"type": "text", "text": json.dumps({"detections": detections})}
                    ]
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))

            except Exception as e:
                print(f"Error: {e}")
                import traceback

                traceback.print_exc()
                self.send_response(500)
                self.end_headers()
                error_response = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"detections": [], "error": str(e)}),
                        }
                    ]
                }
                self.wfile.write(json.dumps(error_response).encode("utf-8"))
        else:
            self.send_error(404, "Endpoint not found")


if __name__ == "__main__":
    print("Server running on port 8000...")
    print(f"Loading YOLO model from: {MODEL_PATH}")
    print(f"Model classes: {model.names}")
    print(f"Confidence threshold: {MIN_THRESH}")

    httpd = HTTPServer(("localhost", 8000), CORSRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()
