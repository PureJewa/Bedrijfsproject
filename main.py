import customtkinter as ctk
from config import *  # Import all configuration values (like button names, IP, etc.)
import datetime
from logger import set_gui_instance, write_log  # Functions to log events in the GUI
from tia_connection import TIAConnection, sendBool, receiveBool  # Functions to communicate with a PLC

# --- Basic GUI settings ---
ctk.set_appearance_mode("System")  # Set theme (system = matches Windows/Mac theme)
ctk.set_default_color_theme("blue")  # Set default color theme for the GUI
client = TIAConnection(plcIpadress[0], plcIpadress[1], plcIpadress[2])  # Create a connection to the PLC


# --- Main GUI class ---
class Gui(ctk.CTk):  # Our GUI is a subclass of CTk (CustomTkinter main window)
    def __init__(self):
        super().__init__()  # Initialize the parent class (CTk)
        self.lamp = None  # Placeholder for a status indicator (lamp)

        # Register this GUI instance with the logger
        set_gui_instance(self)

        # --- Window setup ---
        self.title("Pick and Place GUI")  # Window title
        self.geometry("800x600")  # Window size (width x height)

        # --- Main layout frames ---
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)

        # Top bar (for navigation buttons)
        self.topbarFrame = ctk.CTkFrame(self.frame, height=50)
        self.topbarFrame.pack(fill="x")

        # Main content area (where screens will be loaded)
        self.contentFrame = ctk.CTkFrame(self.frame)
        self.contentFrame.pack(fill="both", expand=True)

        # --- Default screen ---
        self.create_home_widgets()  # Load the "Home" screen first
        self.create_topbar()  # Create navigation buttons

    # --- What happens when a home button is pressed ---
    def button_action(self, name):
        if name == homeScreenbuttons[0]:  # Start button
            msg = "Starting process..."
            write_log(msg)  # Save message in log
            self.lamp.configure(fg_color=lampColors[0])  # Turn lamp green
            sendBool(client, 1, 0, 1)  # Send "start" signal to PLC
            receiveBool(client, 1, 0, 1)  # Read confirmation from PLC

        elif name == homeScreenbuttons[1]:  # Pause button
            msg = "Pausing process..."
            write_log(msg)
            self.lamp.configure(fg_color=lampColors[1])  # Turn lamp yellow

        elif name == homeScreenbuttons[2]:  # Stop button
            msg = "Stopping process..."
            write_log(msg)
            self.lamp.configure(fg_color=lampColors[2])  # Turn lamp red

    # --- Switch between screens ---
    def switch_screen(self, screen_name):
        # Remove everything currently shown in the content frame
        for widget in self.contentFrame.winfo_children():
            widget.destroy()

        # Load new screen depending on button pressed
        if screen_name == topButtons[0]:  # Home
            self.create_home_widgets()
        elif screen_name == topButtons[1]:  # Settings
            self.create_settings_widgets()
        elif screen_name == topButtons[2]:  # Log screen
            self.logScreen = ctk.CTkToplevel(self)  # Open new window
            self.logScreen.title("Log Screen")
            self.logScreen.geometry("500x400")
            self.logScreen.attributes("-topmost", True)  # Keep log window on top

            # Add a textbox to display logs
            self.log_textbox = ctk.CTkTextbox(self.logScreen, width=500, height=400)
            self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)

            # Load logs only from this session
            from logger import session_logs
            for line in session_logs:
                self.log_textbox.insert("end", line)

    # --- Create the top navigation bar ---
    def create_topbar(self):
        for i, btn in enumerate(topButtons):
            # Create a button for each option in topButtons
            btn = ctk.CTkButton(
                self.topbarFrame,
                text=btn.capitalize(),
                command=lambda b=btn: self.switch_screen(b)  # Switch screen when clicked
            )
            btn.grid(row=0, column=i, padx=2, pady=5, sticky="nsew")

        # Make sure all buttons share space equally
        self.topbarFrame.grid_columnconfigure(tuple(range(len(topButtons))), weight=1)

    # --- Create widgets for the home screen ---
    def create_home_widgets(self):
        # Left side = Control area
        self.controlFrame = ctk.CTkFrame(self.contentFrame)
        self.controlFrame.pack(fill='both', expand=True, side="left", padx=20, pady=20)

        # Right side = Overview area
        self.overviewFrame = ctk.CTkFrame(self.contentFrame)
        self.overviewFrame.pack(fill='both', expand=True, side="right", padx=20, pady=20)

        # Title label
        homeScreenLabel = ctk.CTkLabel(self.controlFrame, text="Home Screen", font=ctk.CTkFont(size=20, weight="bold"))
        homeScreenLabel.pack(pady=10)

        # Buttons (start, pause, stop)
        for btn in homeScreenbuttons:
            btn = ctk.CTkButton(self.controlFrame, text=btn.capitalize(), command=lambda b=btn: self.button_action(b))
            btn.pack(pady=5)

        # Machine status label
        statusLabel = ctk.CTkLabel(self.controlFrame, text="Status machine:")
        statusLabel.pack(pady=10)

        # Status lamp (circle that changes color: gray → green/yellow/red)
        self.lamp = ctk.CTkLabel(self.controlFrame, text="", width=50, height=50, fg_color="gray", corner_radius=25)
        self.lamp.pack(pady=5)

        # --- Right side: overview of motors ---
        overviewLabel = ctk.CTkLabel(self.overviewFrame, text="Overview", font=ctk.CTkFont(size=20, weight="bold"))
        overviewLabel.grid(row=0, column=0, columnspan=len(motors), pady=10, sticky="n")

        # Create a label + lamp for each motor
        for i, motor in enumerate(motors):
            motorLabel = ctk.CTkLabel(self.overviewFrame, text=motor)
            motorLabel.grid(row=1, column=i, padx=10, pady=5)

            motorLamp = ctk.CTkLabel(self.overviewFrame, text="", width=30, height=30, fg_color="gray",
                                     corner_radius=15)
            motorLamp.grid(row=2, column=i, padx=10, pady=5)

        # Make sure motor labels distribute evenly
        self.overviewFrame.grid_columnconfigure(tuple(range(len(motors))), weight=1)

    # --- Create settings screen ---
    def create_settings_widgets(self):
        self.settingsFrame = ctk.CTkFrame(self.contentFrame)
        self.settingsFrame.pack(fill='both', expand=True, padx=20, pady=20)

        settingsLabel = ctk.CTkLabel(self.settingsFrame, text="Settings Screen",
                                     font=ctk.CTkFont(size=20, weight="bold"))
        settingsLabel.pack(pady=20)


# --- Start the program ---
gui_instance = Gui()
gui_instance.mainloop()
