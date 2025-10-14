import cv2
from logger import write_log
class Vision:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise write_log(f"Camera with index {self.camera_index} could not be opened.")

    def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise write_log("Failed to capture frame from camera.")
        return frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()