import cv2
from Python_code.Logger.logger import write_log
import threading
class Vision:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()

    def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            write_log("Failed to capture frame from camera.")
            self.running = False  # netjes stoppen
            return None
        return frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def run(self):
        self.running = True
        while self.running:
            frame = self.capture_frame()
            if frame is None:
                break  # stop loop
            # processing...
