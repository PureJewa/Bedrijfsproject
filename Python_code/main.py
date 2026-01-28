# main.py
# Imports from python libs
import threading
import time
import cv2

# Imports within the project
from Python_code.GUI.App import Gui
from Python_code.Communication.communicationTia import plc_connect
from Python_code.Communication.state_machine import PLCSequence
from Python_code.Logger.logger import write_log
from Python_code.Vision.Vision import Vision

vision_app = Vision()

def run_plc(gui_app):
    """
    Make a connection to the PLC.
    :param gui_app:
    """

    if plc_connect():
        write_log("Connected to PLC successfully.")
        gui_app.device_status["PLC"] = "ok"
    else:
        write_log("Failed to connect to PLC.")
        gui_app.device_status["PLC"] = "error"

def plc_worker(vision_app, gui_app):
    seq = PLCSequence(vision_app, gui_app)
    while True:
        seq.step()
        time.sleep(0.05)

def camera_worker(gui_app, cam_index=1):
    gui_app.camera_thread_alive = True
    gui_app.camera_connected = False
    gui_app.latest_frame = None

    cap = None
    last_camera_state = None

    while gui_app.camera_thread_alive:

        # ───────────── Camera openen ─────────────
        if not gui_app.camera_connected:
            cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)

            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FPS, 30)
                gui_app.camera_connected = True
                gui_app.device_status["Camera"] = "ok"

                if last_camera_state != "connected":
                    write_log("Camera connected")
                    last_camera_state = "connected"
            else:
                gui_app.device_status["Camera"] = "error"
                time.sleep(1)
                continue

        # ───────────── Frame lezen ─────────────
        ret, frame = cap.read()

        if not ret or frame is None:
            gui_app.camera_connected = False
            gui_app.device_status["Camera"] = "error"

            if last_camera_state != "disconnected":
                write_log("Camera disconnected")
                last_camera_state = "disconnected"

            cap.release()
            cap = None
            time.sleep(1)
            continue

        # ───────────── GUI frame (RGB) ─────────────
        gui_app.latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ───────────── Vision frame (BGR) ─────────────
        # Vision mag alleen meekijken, nooit camera openen
        if vision_app.active:
            vision_app.process_frame(frame)

        time.sleep(0.005)

    # ───────────── Netjes afsluiten ─────────────
    if cap:
        cap.release()


def run_vision(gui_app):
    while True:
        if gui_app.startVision:
            vision_app.start()
        time.sleep(0.1)




if __name__ == "__main__":
    # Start de GUI in de main-thread
    app = Gui()

    # Verind met PLC in apparte thread
    threading.Thread(target=run_plc, args=(app,), daemon=True).start()
    #
    # Start Vision in aparte thread
    threading.Thread(target=run_vision, args=(app,), daemon=True).start()
    threading.Thread(target=plc_worker, args=(vision_app,app,), daemon=True).start()
    threading.Thread(target=camera_worker, args=(app, 1), daemon=True).start()
    app.mainloop()

