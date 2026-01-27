import customtkinter as ctk
from Python_code.GUI.screens.config_screens import *
from Python_code.Logger.logger import write_log
from Python_code.Communication.communicationConfig import *
from Python_code.Communication.communicationTia import *

def create_test_widgets(app):
    app.testFrame = ctk.CTkFrame(app.contentFrame)
    app.testFrame.pack(fill='both', expand=True, padx=20, pady=20)

    for btn in testButtons:
        button = ctk.CTkButton(app.testFrame, text=btn, command=lambda b=btn: test_button_action(b))
        button.pack(pady=5)

def test_button_action(button_name):
    set_bit(button_name, True)
    write_log(f"Test button '{button_name}' pressed.")

    if button_name == "QR_Read_PLC":
        qr_done = get_bit("QR_Read_PLC")
        write_log(f"QRDone status: {qr_done}")
