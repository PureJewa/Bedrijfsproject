# logger.py
import datetime

gui_instance = None
session_logs = []

def set_gui_instance(instance):
    global gui_instance
    gui_instance = instance

def write_log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"

    # Bestand
    with open("session.log", "a") as f:
        f.write(log_line)

    # Session buffer
    session_logs.append(log_line)

    # GUI update
    if gui_instance and hasattr(gui_instance, "log_textbox"):
        gui_instance.log_textbox.insert("end", log_line)
        gui_instance.log_textbox.see("end")
