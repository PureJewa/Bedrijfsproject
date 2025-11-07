import customtkinter as ctk
import subprocess
from config import *  # Import all configuration values (like button names, IP, etc.)
from logger import set_gui_instance  # Functions to log events in the GUI
from tia_connection import *  # Functions to communicate with a PLC
# from Python_code.GUI.Vision import *
from plc_controller_window import App

# --- Basic GUI settings ---
ctk.set_appearance_mode("System")  # Set theme (system = matches Windows/Mac theme)
ctk.set_default_color_theme("blue")  # Set default color theme for the GUI

# client = TIAConnection(plcIpadress[0], plcIpadress[1], plcIpadress[2])  # Create a connection to the PLC
# # client = TIAConnection(*plcIpadress)
# print(*plcIpadress)

# --- Main GUI class ---
class Gui(ctk.CTk):  # Our GUI is a subclass of CTk (CustomTkinter main window)
    def __init__(self):
        super().__init__()  # Initialize the parent class (CTk)
        self.lamp = None  # Placeholder for a status indicator (lamp)
        self.logScreen = None  # Placeholder for the log screen window
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
        try:
            if name == homeScreenbuttons[0]:  # Start button
                msg = "Starting process..."
                write_log(msg)  # Save message in log
                self.lamp.configure(fg_color=lampColors[0])  # Turn lamp green
                # sendBool(client, 1, 0, 1, True)  # Send "start" signal to PLC
                write_bool(*startPLC, True)
                if not receiveBool(client, 1, 0, 1): # Read confirmation from PLC
                    msg = 'didnt recieve bool'
                    write_log(msg)
                    sendBool(client, 1, 0, 1, True)

                    if not receiveBool(client, 1, 0, 1):
                        msg = '2nd time didnt recieve bool'
                        write_log(msg)

            elif name == homeScreenbuttons[1]:  # Pause button
                msg = "Pausing process..."
                write_log(msg)
                self.lamp.configure(fg_color=lampColors[1])  # Turn lamp yellow
                sendBool(client, *pausePLC, True)  # Send "pause" signal to PLC

            elif name == homeScreenbuttons[2]:  # Stop button
                msg = "Stopping process..."
                write_log(msg)
                self.lamp.configure(fg_color=lampColors[2])  # Turn lamp red
                sendBool(client, *stopPLC, True)  # Send "stop" signal to PLC
            elif name == homeScreenbuttons[4]: # Reset button
                msg = "Resetting process..."
                write_log(msg)
                self.lamp.configure(fg_color="gray")
            elif name == homeScreenbuttons[5]:
                msg = 'Start camera'
                write_log(msg)
                subprocess.Popen("python Python_code\\GUI\\Vision.py", shell=True)  # Start the vision script in a new process
            elif name == homeScreenbuttons[3]:
                msg = "Homing process..."
                write_log(msg)
                self.lamp.configure(fg_color="blue")
                write_bool(*homePLC, True)


        except Exception as e:
            write_log(f"Error in button_action: {e}")

    def test_button_action(self, name):
        try:
            # if name == testButtons[0]:
            #     sendBool(client, 1, 0, 0, True)
            #     msg = "Sent Bool True to DB1.DBX0.0"
            #     write_log(msg)
            # elif name == testButtons[1]:
            #     value = receiveBool(client, 1, 0, 0)
            #     msg = f"Received Bool from DB1.DBX0.0: {value}"
            #     write_log(msg)
            # elif name == testButtons[2]:
            #     sendInt(client, 1, 6, 12345)
            #     msg = "Sent Int 12345 to DB1.DBW2"
            #     write_log(msg)
            # elif name == testButtons[3]:
            #     value = receiveInt(client, 1, 6)
            #     msg = f"Received Int from DB1.DBW2: {value}"
            #     write_log(msg)
            # elif name == testButtons[4]:
            #     sendFloat(client, 1, 2, 12.34)
            #     msg = "Sent Float 12.34 to DB1.DBD4"
            #     write_log(msg)
            # elif name == testButtons[5]:
            #     value = receiveFloat(client, 1, 2)
            #     msg = f"Received Float from DB1.DBD4: {value}"
            #     write_log(msg)
            # elif name == testButtons[6]:
            #     sendString(client, 1, 8, "Hello PLC")
            #     msg = "Sent String 'Hello PLC' to DB1.DBB8"
            #     write_log(msg)
            # elif name == testButtons[7]:
            #     value = receiveString(client, 1, 8, 20)
            #     msg = f"Received String from DB1.DBB8: {value}"
            #     write_log(msg)
            #
            # elif name == testButtons[8]:
            #     sendLreal(client, 1, 10, "35.45")
            #     msg = "Sent Lreal [45, 90, 135] to DB1.DBB8"
            #     write_log(msg)
            # elif name == testButtons[9]:
            #     value = recieveLreal(client, 1, 10, 20)
            #     msg = f"Sent Lreal  from DB1.DBB8: {value}"
            #     write_log(msg)
            if name == testButtons[0]:
                write_bool(*Forward_X, True)
                msg = "Moving X axis forward"
                write_log(msg)
            if name == testButtons[1]:
                write_bool(*Backward_X, True)
                msg = "Moving X axis backward"
                write_log(msg)
            if name == testButtons[2]:
                write_bool(*Forward_Y, True)
                msg = "Moving Y axis forward"
                write_log(msg)
            if name == testButtons[3]:
                write_bool(*Backward_Y, True)
                msg = "Moving Y axis backward"
                write_log(msg)
            if name == testButtons[4]:
                write_bool(*Forward_Z, True)
                msg = "Moving Z axis forward"
                write_log(msg)
            if name == testButtons[5]:
                write_bool(*Backward_Z, True)
                msg = "Moving Z axis backward"
                write_log(msg)
            if name == testButtons[6]:
                x_coord = write_lreal(*X_CoordinatePLC)
                msg = f"X Coordinate: {x_coord}"
                write_log(msg)
            if name == testButtons[7]:
                y_coord = write_lreal(*Y_CoordinatePLC)
                msg = f"Y Coordinate: {y_coord}"
                write_log(msg)
            if name == testButtons[8]:
                z_coord = write_lreal(*Z_CoordinatePLC)
                msg = f"Z Coordinate: {z_coord}"
                write_log(msg)
            if name == testButtons[9]:
                write_lreal(*X_Speed)
                msg = "Set X Speed to 100 mm/s"
                write_log(msg)
            if name == testButtons[10]:
                write_lreal(*Y_Speed)
                msg = "Set Y Speed to 100 mm/s"
                write_log(msg)
            if name == testButtons[11]:
                write_lreal(*Z_Speed)
                msg = "Set Z Speed to 100 mm/s"
                write_log(msg)

        except Exception as e:
            write_log(f"Error in button_action: {e}")
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
        elif screen_name == topButtons[3]: # Test screen
            self.create_test_widgets()
        elif screen_name == topButtons[4]: # Control PLC
            msg = "Opening PLC controller..."
            write_log(msg)
            subprocess.Popen("python Python_code\\GUI\\plc_controller_window.py", shell=True)



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
        self.device_lamps = {}

        for i, device in enumerate(devices):
            deviceLabel = ctk.CTkLabel(self.overviewFrame, text=device)
            deviceLabel.grid(row=i+1, column=1, padx=10, pady=5)

            lamp = ctk.CTkLabel(self.overviewFrame, text="", width=30, height=30,
                                fg_color="gray", corner_radius=15)
            lamp.grid(row=i+1, column=2, padx=10, pady=5)

            self.device_lamps[device] = lamp

        # Make sure motor labels distribute evenly
        self.overviewFrame.grid_columnconfigure(tuple(range(len(motors))), weight=1)
        # Start het proces
        self.update_lamp()

    def update_lamp(self):
        # Stop de callback als het venster of de lampen zijn vernietigd
        if not self.winfo_exists():
            return

        try:
            raw = read_bits_bytes()
            b = raw[0]
            bit_val = (b >> 1) & 0x01

            for motor in ["X-motor", "Y-motor", "Z-motor"]:
                lamp = self.device_lamps.get(motor)
                if lamp and lamp.winfo_exists():
                    lamp.configure(fg_color="green" if bit_val == 1 else "red")

        except Exception as e:
            # Als de GUI net sluit, negeer dan de fout (voorkomt crash)
            print(f"update_lamp error: {e}")

        # Alleen opnieuw aanroepen als het venster nog bestaat
        if self.winfo_exists():
            self.after(100, self.update_lamp)

    # --- Create settings screen ---
    def create_settings_widgets(self):
        self.settingsFrame = ctk.CTkFrame(self.contentFrame)
        self.settingsFrame.pack(fill='both', expand=True, padx=20, pady=20)

        settingsLabel = ctk.CTkLabel(self.settingsFrame, text="Settings Screen",
                                     font=ctk.CTkFont(size=20, weight="bold"))
        settingsLabel.pack(pady=20)

        self.speedEntry = ctk.CTkEntry(self.settingsFrame, placeholder_text="Enter speed (mm/s)")
        self.speedEntry.pack(pady=10)
        self.speedEntryButton = ctk.CTkButton(self.settingsFrame, text="Set Speed", command=lambda :self.set_speed(self.speedEntry.get()))
        self.speedEntryButton.pack(pady=5)
        self.accelerationEntry = ctk.CTkEntry(self.settingsFrame, placeholder_text="Enter acceleration (mm/s²)")
        self.accelerationEntry.pack(pady=10)
        self.accelerationEntryButton = ctk.CTkButton(self.settingsFrame, text="Set Acceleration", command=lambda :self.set_acceleration(self.accelerationEntry.get()))
        self.accelerationEntryButton.pack(pady=5)

        self.cyclesEntry = ctk.CTkEntry(self.settingsFrame, placeholder_text="Enter number of cycles")
        self.cyclesEntry.pack(pady=10)
        self.cyclesEntryButton = ctk.CTkButton(self.settingsFrame, text="Set Cycles", command=lambda :self.set_cycles(self.cyclesEntry.get()))
        self.cyclesEntryButton.pack(pady=5)


    def set_speed(self, speed):
        try:
            speed_value = float(speed)
            if speed_value <= 0:
                raise ValueError("Speed must be a positive number.")
            msg = f"Speed set to {speed_value} mm/s"
            write_log(msg)
            sendFloat(client, *speedPLC, speed_value)
        except ValueError as ve:
            write_log(f"Invalid speed input: {ve}")
        except Exception as e:
            write_log(f"Error setting speed: {e}")

    def set_cycles(self, cycles):
        try:
            cycles_value = int(cycles)
            if cycles_value <= 0:
                raise ValueError("Number of cycles must be a positive integer.")
            msg = f"Number of cycles set to {cycles_value}"
            write_log(msg)
            sendInt(client, *cyclesPLC, cycles_value)
        except ValueError as ve:
            write_log(f"Invalid cycles input: {ve}")
        except Exception as e:
            write_log(f"Error setting number of cycles: {e}")
    def set_acceleration(self, acceleration):
        try:
            acceleration_value = float(acceleration)
            if acceleration_value <= 0:
                raise ValueError("Acceleration must be a positive number.")
            msg = f"Acceleration set to {acceleration_value} mm/s²"
            write_log(msg)
            sendFloat(client, *accelerationPLC, acceleration_value)
        except ValueError as ve:
            write_log(f"Invalid acceleration input: {ve}")
        except Exception as e:
            write_log(f"Error setting acceleration: {e}")
    def create_test_widgets(self):
        self.testFrame = ctk.CTkFrame(self.contentFrame)
        self.testFrame.pack(fill='both', expand=True, padx=20, pady=20)


        for btn in testButtons:
            button = ctk.CTkButton(self.testFrame, text=btn, command=lambda b=btn: self.test_button_action(b))
            button.pack(pady=5)

# --- Start the program ---
gui_instance = Gui()
gui_instance.mainloop()

