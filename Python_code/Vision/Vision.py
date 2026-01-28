import cv2
import threading
import json

import ast
from datetime import datetime
from Python_code.Logger.logger import write_log
class Vision:
    def __init__(self, json_path="qr_data.json"):
        self.qr_detector = cv2.QRCodeDetector()

        self.coords = None
        self.lock = threading.Lock()

        self.json_path = json_path
        self.active = False   # wordt gezet door GUI / PLC

    def start(self):
        """Vision activeren (geen thread!)"""
        self.active = True

    def stop(self):
        self.active = False

    def process_frame(self, frame):
        if not self.active or self.coords is not None:
            return

        if frame is None or frame.size == 0:
            return

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except cv2.error:
            return

        h, w = gray.shape
        if h < 50 or w < 50:
            return  # te klein / corrupt frame

        # Veilige resize
        if w > 800:
            scale = 800 / float(w)
            new_h = int(h * scale)
            if new_h <= 0:
                return
            gray = cv2.resize(gray, (800, new_h), interpolation=cv2.INTER_AREA)

        try:
            data, bbox, _ = self.qr_detector.detectAndDecode(gray)
        except cv2.error as e:
            write_log(f"Vision: OpenCV QR error: {e}")
            return

        if not data:
            return

        write_log(f"Vision: QR detected, raw data length={len(data)}")

        parsed = self.parse_table(data)
        if not parsed:
            write_log("Vision: QR detected but parsing failed")
            return

        with self.lock:
            self.coords = parsed

        self.save_to_json(parsed)
        write_log("Vision: QR parsed and JSON saved")

        self.active = False


    def parse_table(self, data: str):
        """
        Verwacht QR-data in vorm van een Python-lijst als string:
        ['3-1:929:562', '4-1:1020:340', ...]
        """
        data = data.strip()

        try:
            items = ast.literal_eval(data)
        except Exception as e:
            write_log(f"Vision: failed to eval QR data: {e}")
            return None

        if not isinstance(items, list):
            write_log("Vision: QR data is not a list")
            return None

        result = []

        for i, item in enumerate(items, start=1):
            if not isinstance(item, str):
                write_log(f"Vision: non-string item at index {i}: {item}")
                continue

            parts = item.split(":")
            if len(parts) != 3:
                write_log(f"Vision: invalid item format at index {i}: {repr(item)}")
                continue

            try:
                result.append({
                    "id": parts[0],
                    "x": int(parts[1]),
                    "y": int(parts[2])
                })
            except ValueError:
                write_log(f"Vision: value error at index {i}: {repr(item)}")
                continue

        if not result:
            write_log("Vision: no valid coordinate rows parsed")
            return None

        return result

    def save_to_json(self, points):
        payload = {
            "timestamp": datetime.now().isoformat(),
            "points": points
        }

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

    def get_coordinates(self):
        with self.lock:
            return self.coords

    def reset(self):
        with self.lock:
            self.coords = None
