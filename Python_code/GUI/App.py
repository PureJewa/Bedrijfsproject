# App.py

# Imports from python libs
import customtkinter as ctk
import tkinter as tk
import subprocess

# Imports within the project
from Python_code.GUI.screens.config_screens import *
from Python_code.GUI.screens.home_screen import *
from Python_code.GUI.screens.settings_screen import *
from Python_code.GUI.screens.test_screen import *
from Python_code.GUI.screens.control_screen import *
from Python_code.GUI.screens.log_screen import *
from Python_code.Logger.logger import *
from Python_code.Communication.communicationTia import *
from Python_code.Communication.communicationConfig import *

# Basic GUI settings
ctk.set_appearance_mode("System")  # Set theme (system = matches Windows/Mac theme)
ctk.set_default_color_theme("blue")  # Set default color theme for the GUI


# Main GUI class
class Gui(ctk.CTk):  # Our GUI is a subclass of CTk (CustomTkinter main window)
    def __init__(self):
        super().__init__()  # Initialize the parent class (CTk)
        # Init parameters
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.startVision = None
        self.operationSwitch = False
        self.connectionToPLC = None
        self.connectionToCamera = None
        self.lamp = None
        self.logScreen = None
        self.magnet_on = False
        self.camera_connected = None
        self.device_status = {
            "PLC": "unknown",
            "X-motor" : "NA",
            "Y-motor": "NA",
            "Z-motor": "NA",
            "Gripper": "NA",
            "Camera": "unknown",
            "X-endstop" : "NA",
            "Y-endstop": "NA",
            "Z-endstop": "NA",
        }

        self.device_lamps = {}

        self.topbar_buttons = {}
        self.control_buttons = {}
        self.lreal_entries = {}
        self.input_entries = {}
        self.accelerationEntryX = None
        self.accelerationEntryY = None
        self.accelerationEntryZ = None
        self.value = 0
        self.processedAmount = 0
        self.acceleration_entries = {
            "X": self.accelerationEntryX,
            "Y": self.accelerationEntryY,
            "Z": self.accelerationEntryZ
        }
        self.homeScreenStatusLabel = ctk.CTkLabel
        self.switch = ctk.CTkSwitch
        self.operation_mode_var = ctk.BooleanVar(value=self.operationSwitch)

        # This is for the joystick control
        self.axis_last_bits_sign = {"X": 0, "Y": 0, "Z": 0}
        self.last_state = {name: None for name in BITS_ALL.keys()}
        self.last_speed = {
            "Joystick_X_speed": None,
            "Joystick_Y_speed": None,
            "Joystick_Z_speed": None,
        }

        # Direction, based on the bits, -1/0/1
        self.axis_last_bits_sign = {"X": 0, "Y": 0, "Z": 0}
        self.status_lbl = ctk.CTkLabel(self)

        # Show current value
        self.pct_x = tk.StringVar(value="0%")
        self.pct_y = tk.StringVar(value="0%")
        self.pct_z = tk.StringVar(value="0%")
        self.pct_r = tk.StringVar(value="0%")
        self.deadzone = tk.DoubleVar(value=0.20)
        self.threshold = tk.DoubleVar(value=0.30)

        # Register this GUI instance with the logger
        set_gui_instance(self)

        # Window setup
        self.title("Pick and Place GUI")  # Window title
        self.geometry(f"{self.screen_width}x{self.screen_height}")  # Window size (width x height)

        # Mainframe
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)

        # Top bar
        self.topbarFrame = ctk.CTkFrame(self.frame, height=50, border_width=2, fg_color="#2d2d2f")
        self.topbarFrame.pack(fill="x")

        # Main content area (where screens will be loaded)
        self.contentFrame = ctk.CTkFrame(self.frame, fg_color="#1b1b1c")
        self.contentFrame.pack(fill="both", expand=True)

        # Default screen
        self.create_topbar()  # Create navigation buttons
        create_home_widgets(self)  # Load the "Home" screen first
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        #  Check if gui instance is made
        if self.winfo_exists():
            write_log("GUI opgestart")
        # Update topbar button highlight
        self.highlight_topbar_button("Home")

        self.update_devices()

    # Create the top navigation bar
    def create_topbar(self):
        """
        Makes the navigation bar at the top of the frame
        To add buttons expand the topButtons in config_screens.py
        To add functionality add the function to self.switch_screen()
        """

        for i, name in enumerate(topButtons):
            # Create a button for each option in topButtons
            button = ctk.CTkButton(
                self.topbarFrame,
                text=name,
                height=75,
                font=("", 16),
                command=lambda n=name: self.switch_screen(n),
                border_width=4,
                border_color="#242425"
            )
            button.grid(row=0, column=i, padx=2, pady=5, sticky="nsew")

            # Store reference for later use (highlighting)
            self.topbar_buttons[name] = button

        # Make sure all buttons share space equally
        for col in range(len(topButtons)):
            self.topbarFrame.grid_columnconfigure(col, weight=1)

    def switch_screen(self, screen_name):
        """
        Function to switch screens
        First check which button is pressed
        Then remove widgets except when log button is pressed
        Then call function of relevant screen
        :param screen_name:
        """
        # Update topbar button highlight
        self.highlight_topbar_button(screen_name)

        # Load new screen depending on button pressed
        if screen_name == "Home":
            # Remove everything currently shown in the content frame
            for widget in self.contentFrame.winfo_children():
                widget.pack_forget()
            create_home_widgets(self)

        elif screen_name == "Settings":
            # Remove everything currently shown in the content frame
            for widget in self.contentFrame.winfo_children():
                widget.pack_forget()
            create_settings_widgets(self)

        elif screen_name == "Log":
            create_log_widgets(self)

        elif screen_name == "Test":
            # Remove everything currently shown in the content frame
            for widget in self.contentFrame.winfo_children():
                widget.pack_forget()
            create_test_widgets(self)

        elif screen_name == "Control PLC":
            # Remove everything currently shown in the content frame
            write_log("Opening PLC controller")
            for widget in self.contentFrame.winfo_children():
                widget.pack_forget()
            create_control_widgets(self)

    def on_close(self):
        """
        Tells PLC to stop motion
        Disconnects from PLC
        Shuts down the GUI properly
        """
        self.motion_off()
        plc_disconnect()
        self.destroy()

    def motion_off(self):
        """
        Sets all motion bits to false and all speeds to 0
        """
        for name in BITS_ALL:
            set_bit(name, False)

        write_lreal("Joystick_X_speed", 0.0)
        write_lreal("Joystick_Y_speed", 0.0)
        write_lreal("Joystick_Z_speed", 0.0)

    def make_line(self, frame):
        return ctk.CTkFrame(frame, height=2, fg_color="gray")

    def highlight_topbar_button(self, active_name):
        """
        Visually highlights the currently active topbar button.

        Parameters
        ----------
        active_name : str
            Name of the button that should be highlighted.
        """
        for name, button in self.topbar_buttons.items():

            if name == active_name:
                button.configure(fg_color="#1F6AA5")  # active color
            else:
                button.configure(fg_color="#3E3E40")  # default color

    def update_devices(self):
        for device, status in self.device_status.items():
            lamp = self.device_lamps.get(device)
            if not lamp:
                continue

            if status == "ok":
                lamp.configure(fg_color="green")
            elif status == "error":
                lamp.configure(fg_color="red")
            elif status == "NA":
                lamp.configure(fg_color="gray")
            else:
                lamp.configure(fg_color="blue")

        self.after(100, self.update_devices)

