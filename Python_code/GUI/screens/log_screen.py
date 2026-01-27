# log_screen.py

# Imports from python libs
import customtkinter as ctk

# Imports within the project
from Python_code.Logger.logger import session_logs

def create_log_widgets(app):
    """
    Create the log screen widgets.
    :param app: Instance of the main application
    :return:
    """

    # Create a new top-level window for the log screen, always on top
    app.logScreen = ctk.CTkToplevel(app)
    app.logScreen.title("Log Screen")
    app.logScreen.geometry("500x400")
    app.logScreen.attributes("-topmost", True)

    # Add a textbox to display logs
    app.log_textbox = ctk.CTkTextbox(app.logScreen, width=500, height=400)
    app.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)

    # Load logs only from this session
    for line in session_logs:
        app.log_textbox.insert("end", line)
