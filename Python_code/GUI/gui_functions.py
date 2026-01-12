from screens.config_screens import topButtons
import customtkinter as ctk
def sendback(widget):
    return widget
# --- Switch between screens ---
def switch_screen(self, screen_name):


    # Load new screen depending on button pressed
    if screen_name == topButtons[0]:  # Home
        # Remove everything currently shown in the content frame
        for widget in self.contentFrame.winfo_children():
            widget.destroy()
        self.create_home_widgets()
    elif screen_name == topButtons[1]:  # Settings
        # Remove everything currently shown in the content frame
        for widget in self.contentFrame.winfo_children():
            widget.destroy()
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
        from Python_code.Logger.logger import session_logs
        for line in session_logs:
            self.log_textbox.insert("end", line)
    elif screen_name == topButtons[3]: # Test screen
        # Remove everything currently shown in the content frame
        for widget in self.contentFrame.winfo_children():
            widget.destroy()
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
            command=lambda b=btn: switch_screen(self, b)  # Switch screen when clicked
        )
        btn.grid(row=0, column=i, padx=2, pady=5, sticky="nsew")

    # Make sure all buttons share space equally
    self.topbarFrame.grid_columnconfigure(tuple(range(len(topButtons))), weight=1)
