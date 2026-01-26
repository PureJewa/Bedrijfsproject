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

def camera_worker(gui_app, cam_index=0):
    gui_app.camera_thread_alive = True
    gui_app.camera_connected = False
    gui_app.latest_frame = None

    cap = None

    while gui_app.camera_thread_alive:

        # 1️⃣ Probeer camera te openen als hij er niet is
        if not gui_app.camera_connected:
            cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)

            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FPS, 30)
                gui_app.device_status["Camera"] = 'ok'
                write_log("Camera connected")
            else:
                gui_app.device_status["Camera"] = 'error'
                time.sleep(1)
                continue

        # 2️⃣ Lees frame
        ret, frame = cap.read()

        if not ret:
            # Camera was er, maar is weggevallen
            write_log("Camera disconnected")
            gui_app.camera_connected = False
            cap.release()
            cap = None
            time.sleep(1)
            continue

        # 3️⃣ Verwerk frame
        gui_app.latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        time.sleep(0.005)

    # Thread stopt netjes
    if cap:
        cap.release()

def run_vision(gui_app):
    """
    Start de Vision application when requested by the GUI.
    :param gui_app:
    """
    vision_app = Vision()

    while True:
        if gui_app.startVision and not vision_app.running:
            gui_app.device_lamps["Camera"].configure(fg_color="blue")
            write_log("Starting Vision Application...")
            vision_app.start()
        time.sleep(0.1)
        if vision_app.running:
            gui_app.device_lamps["Camera"].configure(fg_color="green")


def plc_worker():
    seq = PLCSequence()
    while True:
        seq.step()
        time.sleep(0.05)


if __name__ == "__main__":
    # Start de GUI in de main-thread
    app = Gui()

    # Verind met PLC in apparte thread
    threading.Thread(target=run_plc, args=(app,), daemon=True).start()
    #
    # Start Vision in aparte thread
    threading.Thread(target=run_vision, args=(app,), daemon=True).start()
    threading.Thread(target=plc_worker, daemon=True).start()
    threading.Thread(target=camera_worker, args=(app, 1), daemon=True).start()
    app.mainloop()

