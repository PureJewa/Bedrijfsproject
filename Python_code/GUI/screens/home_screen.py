# home_screen.py

# Imports from python libs
import customtkinter as ctk
import subprocess
import time
# Imports within the project
from Python_code.GUI.screens.config_screens import *


def create_home_widgets(app):
    """
    Create the home screen widgets.
    :param app:
    """

    # Hoofdcontainer
    mainFrame = ctk.CTkScrollableFrame(app.contentFrame, fg_color="transparent")
    mainFrame.pack(fill="both", expand=True)

    # Bovenste rij (links + rechts)
    topFrame = ctk.CTkFrame(mainFrame, fg_color="transparent")
    topFrame.pack(fill="both")

    # Make frame for buttons to control the machine (left side)
    controlButtonsFrame = ctk.CTkFrame(topFrame, border_width=1, fg_color="#2d2d2f")
    controlButtonsFrame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
    # Make frame for overview of equipment (right side)
    equipmentLampFrame = ctk.CTkFrame(topFrame, border_width=1, fg_color="#2d2d2f")
    equipmentLampFrame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Make frame for production overvieuw
    productionFrame = ctk.CTkFrame(mainFrame, border_width=2, fg_color="#2d2d2f")
    productionFrame.pack(fill="both", padx=20, pady=20, expand=True)

    # Title label
    homeScreenLabel = ctk.CTkLabel(controlButtonsFrame, text="Home Screen", font=ctk.CTkFont(size=20, weight="bold"))
    homeScreenLabel.pack(pady=10)

    app.homeScreenStatusLabel = ctk.CTkLabel(controlButtonsFrame, text="Ready for use" if app.operation_mode_var.get() else "Turn on operation mode to use")
    app.homeScreenStatusLabel.pack(pady=5)
    # Make sure the machine cant be controlled when programSwitch is off, for safety
    for name in homeScreenButtons:
        button = ctk.CTkButton(controlButtonsFrame, text=name.capitalize(),
                               command=lambda n=name: home_button_action(app, n),
                               state="normal" if app.operationSwitch else "disabled",
                               height=50,
                               fg_color="#096C6C",
                               border_width=7,
                               border_color="#242425"
                               )
        button.pack(pady=5)
        # Store buttons for later use
        app.control_buttons[name] = button

    # Equipment status label
    overviewLabel = ctk.CTkLabel(equipmentLampFrame, text="Device overview", font=ctk.CTkFont(size=20, weight="bold"))
    overviewLabel.grid(row=0, column=0, columnspan=len(motors), pady=10, sticky="n")

    # Create a label + lamp for each piece of equipment
    app.device_lamps = {}

    for i, device in enumerate(devices):
        deviceLabel = ctk.CTkLabel(equipmentLampFrame, text=device)
        deviceLabel.grid(row=i + 1, column=0, padx=5, pady=5, sticky="e")

        lamp = ctk.CTkLabel(equipmentLampFrame, text="", width=30, height=30,
                            fg_color="gray", corner_radius=15)
        lamp.grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")

        # Store buttons for later use
        app.device_lamps[device] = lamp

    if app.connectionToPLC is True:
        app.device_lamps["PLC"].configure(fg_color="green")
    else:
        app.device_lamps["PLC"].configure(fg_color="red")
    # Make sure motor labels distribute evenly
    equipmentLampFrame.grid_columnconfigure(tuple(range(len(motors))), weight=1)

    # app.productionOverview = ProductionOverview(productionFrame, app)
    # Titel
    ctk.CTkLabel(
        productionFrame,
        text="Production overview",
        font=ctk.CTkFont(size=20, weight="bold")
    ).pack(pady=(10, 5))

    # Progress bar
    app.progressBar = ctk.CTkProgressBar(productionFrame)
    app.progressBar.pack(fill="x", padx=20)
    app.progressBar.set(0)

    app.progressLabel = ctk.CTkLabel(productionFrame, text="0 / 100 (0%)")
    app.progressLabel.pack(pady=5)

    # =========================
    # Rij-container (GRID)
    # =========================
    rowFrame = ctk.CTkFrame(productionFrame, fg_color="transparent")
    rowFrame.pack(fill="x", pady=10)

    rowFrame.grid_columnconfigure(0, weight=1)
    rowFrame.grid_columnconfigure(1, weight=1)
    rowFrame.grid_columnconfigure(2, weight=1)

    # Info
    infoFrame = ctk.CTkFrame(rowFrame, fg_color="transparent")
    infoFrame.grid(row=0, column=0, sticky="nsew", padx=10)

    app.statusLabel = ctk.CTkLabel(infoFrame, text="Status: READY" if app.operation_mode_var.get() else "Status: LOCKED")
    app.batchLabel = ctk.CTkLabel(infoFrame, text="Batch: #AAAAA")
    app.productLabel = ctk.CTkLabel(infoFrame, text="Product: Type A")

    app.statusLabel.pack()
    app.batchLabel.pack()
    app.productLabel.pack()

    # Tijd & performance
    statsFrame = ctk.CTkFrame(rowFrame, fg_color="transparent")
    statsFrame.grid(row=0, column=1, sticky="nsew", padx=10)

    app.elapsedLabel = ctk.CTkLabel(statsFrame, text="Time passed: 00:00:00")
    app.remainingLabel = ctk.CTkLabel(statsFrame, text="Time left: --:--:--")
    app.speedLabel = ctk.CTkLabel(statsFrame, text="Speed: 0 amount/min")

    app.elapsedLabel.pack()
    app.remainingLabel.pack()
    app.speedLabel.pack()

    # Kwaliteit
    qualityFrame = ctk.CTkFrame(rowFrame, fg_color="transparent")
    qualityFrame.grid(row=0, column=2, sticky="nsew", padx=10)

    app.amountLabel = ctk.CTkLabel(qualityFrame, text=f"Set amount: {app.value}")
    app.processed = ctk.CTkLabel(qualityFrame, text=f"Processed: {app.processedAmount}")
    app.errorLabel = ctk.CTkLabel(qualityFrame, text="Laatste fout: -")

    app.amountLabel.pack()
    app.processed.pack()
    app.errorLabel.pack()

    # ctk.CTkLabel(productionFrame, text="Progress", font=ctk.CTkFont(size=20, weight="bold")).pack(padx=5, pady=5)
    # app.progressBar = ctk.CTkProgressBar(productionFrame)
    # app.progressBar.pack()
    # Keep checking connection status

    # confirm_connection(app)


def home_button_action(app, name):
    """
    Handles actions triggered by buttons on the home screen.

    This function translates a GUI button press into a PLC command by:
    - Writing a log message
    - Setting the corresponding PLC control bit
    - Resetting conflicting PLC control bits
    - Verifying whether the PLC acknowledged the command

    Special case:
    - The 'Camera' button starts the vision system as a separate process
      and does not interact with the PLC.
    :param app: Instance ob main application
    :param app: Name of button
    """
    highlight_homescreen_button(app, name)
    try:

        # Handle camera action separately (no PLC interaction)
        if name == "Camera":
            write_log("Start camera")

            # Start the vision script as a separate process
            subprocess.Popen(
                "python Python_code\\Vision\\Vision.py",
                shell=True
            )

            # Store vision state in the application instance
            app.startVision = True
            return

        # Retrieve the action configuration for the pressed button
        action = ACTIONS.get(name)
        if action is None:
            # Unknown button name; do not perform any PLC action
            write_log(f"Unknown button action: {name}")
            return

        # Write the corresponding action log
        write_log(action["log"])

        # Activate the PLC control bit associated with this action
        set_bit(action["bit"], True)

        # Reset all mutually exclusive PLC control bits
        for bit in action["reset"]:
            set_bit(bit, False)

        # Verify whether the PLC acknowledged the command
        confirmed = get_bit(action["bit"])
        if not confirmed:
            write_log(f"{name} confirmation not received from PLC")

    except Exception as e:
        # Catch any unexpected runtime errors to prevent GUI crashes
        write_log(f"Error in home_button_action: {e}")


def confirm_connection(app):
    """
    Confirm the connection to the PLC and update lamps accordingly.
    :param app: Instance of the main application
    """

    # Check if the app window still exists
    if not app.winfo_exists():
        return

    try:
        if app.connectionToPLC is not None:
            app.lamp.configure(fg_color="green" if app.connectionToPLC else "red")

            # Update device lamps
            for i, device in enumerate(devices):
                bit_val = get_bit(f"{device}")
                lamp = app.device_lamps.get(device)
                if lamp and lamp.winfo_exists():
                    lamp.configure(fg_color="green" if bit_val == 1 else "red")

    except Exception as e:
        write_log(f"update lamp error: {e}")

    # Schedule the next check
    if app.winfo_exists():
        app.after(500, lambda: confirm_connection(app))

def highlight_homescreen_button(app, active_name):
    """
    Visually highlights the currently active topbar button.

    Parameters
    ----------
    active_name : str
        Name of the button that should be highlighted.
    """
    for name, button in app.control_buttons.items():
        if name == active_name:
            button.configure(fg_color="#1F6AA5")  # active color
        else:
            button.configure(fg_color="#3E3E40")  # default color
class ProductionOverview:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.start_time = time.time()
        self.total_items = 100
        self.completed = 0
        self.rejected = 0
        self.running = True

        self.build_ui()
        self.update_loop()

    def build_ui(self):
        # Titel
        ctk.CTkLabel(
            self.parent,
            text="Productie-overzicht",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(10, 5))

        # Progress bar
        self.progressBar = ctk.CTkProgressBar(self.parent)
        self.progressBar.pack(fill="x", padx=20)
        self.progressBar.set(0)

        self.progressLabel = ctk.CTkLabel(self.parent, text="0 / 100 (0%)")
        self.progressLabel.pack(pady=5)

        # Info
        infoFrame = ctk.CTkFrame(self.parent, fg_color="transparent")
        infoFrame.pack(fill="x", padx=20, pady=10)

        self.statusLabel = ctk.CTkLabel(infoFrame, text="Status: RUNNING")
        self.batchLabel = ctk.CTkLabel(infoFrame, text="Batch: #2026-01")
        self.productLabel = ctk.CTkLabel(infoFrame, text="Product: Type A")

        self.statusLabel.pack(anchor="w")
        self.batchLabel.pack(anchor="w")
        self.productLabel.pack(anchor="w")

        # Tijd & performance
        statsFrame = ctk.CTkFrame(self.parent, fg_color="transparent")
        statsFrame.pack(fill="x", padx=20, pady=10)

        self.elapsedLabel = ctk.CTkLabel(statsFrame, text="Verstreken tijd: 00:00:00")
        self.remainingLabel = ctk.CTkLabel(statsFrame, text="Resterende tijd: --:--:--")
        self.speedLabel = ctk.CTkLabel(statsFrame, text="Snelheid: 0 stuks/min")

        self.elapsedLabel.pack(anchor="w")
        self.remainingLabel.pack(anchor="w")
        self.speedLabel.pack(anchor="w")

        # Kwaliteit
        qualityFrame = ctk.CTkFrame(self.parent, fg_color="transparent")
        qualityFrame.pack(fill="x", padx=20, pady=10)

        self.okLabel = ctk.CTkLabel(qualityFrame, text="Goedgekeurd: 0")
        self.nokLabel = ctk.CTkLabel(qualityFrame, text="Afgekeurd: 0")
        self.errorLabel = ctk.CTkLabel(qualityFrame, text="Laatste fout: -")

        self.okLabel.pack(anchor="w")
        self.nokLabel.pack(anchor="w")
        self.errorLabel.pack(anchor="w")

        # Actieknoppen
        buttonFrame = ctk.CTkFrame(self.parent, fg_color="transparent")
        buttonFrame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(buttonFrame, text="Pauze", command=self.toggle_pause).pack(side="left", padx=5)
        ctk.CTkButton(buttonFrame, text="Stop", command=self.stop).pack(side="left", padx=5)
        ctk.CTkButton(buttonFrame, text="Reset batch", command=self.reset).pack(side="right", padx=5)

    def update_loop(self):
        if self.running and self.completed < self.total_items:
            self.completed += 1
            if self.completed % 15 == 0:
                self.rejected += 1
                self.errorLabel.configure(text="Laatste fout: Sensor X")

        self.update_ui()
        self.parent.after(1000, self.update_loop)

    def update_ui(self):
        progress = self.completed / self.total_items
        self.progressBar.set(progress)
        self.progressLabel.configure(
            text=f"{self.completed} / {self.total_items} ({int(progress * 100)}%)"
        )

        elapsed = int(time.time() - self.start_time)
        speed = self.completed / (elapsed / 60) if elapsed > 0 else 0
        remaining = int((self.total_items - self.completed) / speed * 60) if speed > 0 else 0

        self.elapsedLabel.configure(text=f"Verstreken tijd: {self.format_time(elapsed)}")
        self.remainingLabel.configure(text=f"Resterende tijd: {self.format_time(remaining)}")
        self.speedLabel.configure(text=f"Snelheid: {speed:.1f} stuks/min")

        self.okLabel.configure(text=f"Goedgekeurd: {self.completed - self.rejected}")
        self.nokLabel.configure(text=f"Afgekeurd: {self.rejected}")

        if self.completed >= self.total_items:
            self.statusLabel.configure(text="Status: GEREED")

    def toggle_pause(self):
        self.running = not self.running
        self.statusLabel.configure(
            text="Status: PAUZE" if not self.running else "Status: RUNNING"
        )

    def stop(self):
        self.running = False
        self.statusLabel.configure(text="Status: GESTOPT")

    def reset(self):
        self.start_time = time.time()
        self.completed = 0
        self.rejected = 0
        self.running = True
        self.errorLabel.configure(text="Laatste fout: -")
        self.statusLabel.configure(text="Status: RUNNING")

    @staticmethod
    def format_time(seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02}:{m:02}:{s:02}"
