import customtkinter as ctk
from Python_code.GUI.screens.config_screens import *

def create_test_widgets(app):
    app.testFrame = ctk.CTkFrame(app.contentFrame)
    app.testFrame.pack(fill='both', expand=True, padx=20, pady=20)

    for btn in testButtons:
        button = ctk.CTkButton(app.testFrame, text=btn, command=lambda b=btn: app.test_button_action(b))
        button.pack(pady=5)

def test_button_action(self, button_name):
    write_log(f"Test button '{button_name}' pressed.")