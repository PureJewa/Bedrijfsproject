# main.py

# Imports from python libs
import threading
import time

# Imports within the project
from Python_code.GUI.App import Gui
from Python_code.Communication.communicationTia import plc_connect
from Python_code.Logger.logger import write_log
from Python_code.Vision.Vision import Vision


def run_plc(gui_app):
    """
    Make a connection to the PLC.
    :param gui_app:
    """
    gui_app.device_lamps["PLC"].configure(fg_color="blue")

    if plc_connect():
        write_log("Connected to PLC successfully.")
        gui_app.connectionToPLC = True
        gui_app.device_lamps["PLC"].configure(fg_color="green")

    else:
        write_log("Failed to connect to PLC.")
        gui_app.connectionToPLC = False
        gui_app.device_lamps["PLC"].configure(fg_color="red")


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


if __name__ == "__main__":
    # Start de GUI in de main-thread
    app = Gui()

    # Verind met PLC in apparte thread
    threading.Thread(target=run_plc, args=(app,), daemon=True).start()

    # Start Vision in aparte thread
    threading.Thread(target=run_vision, args=(app,), daemon=True).start()
    app.mainloop()
