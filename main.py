import customtkinter as ctk
from config import *
import datetime
from logger import set_gui_instance, write_log
from tia_connection import TIAConnection, sendData, receiveData

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
client = TIAConnection(plcIpadress[0], plcIpadress[1], plcIpadress[2])

class Gui(ctk.CTk):
    def __init__(self):
        super().__init__()
        set_gui_instance(self)  # Stel de huidige GUI instantie in voor logging
        self.title("Pick and Place GUI")
        self.geometry("800x600")
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)
        self.topbarFrame = ctk.CTkFrame(self.frame, height=50)
        self.topbarFrame.pack(fill="x")
        self.contentFrame = ctk.CTkFrame(self.frame)
        self.contentFrame.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_home_widgets()
        self.create_topbar()

    def button_action(self, name):
        if name == buttons[0]:
            msg = "Starting process..."
            write_log(msg)
            self.lamp.configure(fg_color=lampColors[0])
            sendData(client, 1, 0, 1)
            receiveData(client, 1, 0, 1)
        elif name == buttons[1]:
            msg = "Pausing process..."
            write_log(msg)
            self.lamp.configure(fg_color=lampColors[1])
        elif name == buttons[2]:
            msg = "Stopping process..."
            write_log(msg)
            self.lamp.configure(fg_color=lampColors[2])

    def switch_screen(self, screen_name):
        if screen_name == topButtons[0]:
            self.contentFrame.destroy()
            self.contentFrame = ctk.CTkFrame(self.frame)
            self.contentFrame.pack(fill="both", expand=True, padx=20, pady=20)
            self.create_home_widgets()
        elif screen_name == topButtons[1]:
            self.contentFrame.destroy()
            self.contentFrame = ctk.CTkFrame(self.frame)
            self.contentFrame.pack(fill="both", expand=True, padx=20, pady=20)
            label = ctk.CTkLabel(self.contentFrame, text="Settings Screen")
            label.pack(pady=20)
        elif screen_name == topButtons[2]:
            self.logScreen = ctk.CTkToplevel(self)
            self.logScreen.title("Log Screen")
            self.logScreen.geometry("500x400")
            self.logScreen.attributes("-topmost", True)

            self.log_textbox = ctk.CTkTextbox(self.logScreen, width=500, height=400)
            self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)

            # Alleen huidige sessie inladen
            from logger import session_logs
            for line in session_logs:
                self.log_textbox.insert("end", line)

    def create_topbar(self):
        for i,btn in enumerate(topButtons):
            btn = ctk.CTkButton(self.topbarFrame, text=btn.capitalize(), command=lambda b=btn: self.switch_screen(b))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        self.topbarFrame.grid_columnconfigure(tuple(range(len(topButtons))), weight=1)

    def create_home_widgets(self):
        for btn in buttons:
            btn = ctk.CTkButton(self.contentFrame, text=btn.capitalize(), command=lambda b=btn: self.button_action(b))
            btn.pack(pady=5)
        self.lamp = ctk.CTkLabel(self.contentFrame, text="", width=50, height=50, fg_color="gray", corner_radius=25)
        self.lamp.pack(pady=5)


gui_instance = Gui()
gui_instance.mainloop()