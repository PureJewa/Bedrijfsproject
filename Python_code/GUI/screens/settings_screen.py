# # Settings.py
#
# # Imports from python libs
import customtkinter as ctk
#
# Imports within the project
from Python_code.GUI.screens.config_screens import *

import json

class SettingsEngine:
    def __init__(self, schema_path):
        with open(schema_path, "r") as f:
            self.schema = json.load(f)

    def execute(self, command: str):
        tokens = command.strip().split()
        if not tokens:
            return "Empty command"

        cmd = tokens[0].lower()

        if cmd == "set":
            return self._handle_set(tokens[1:])
        elif cmd == "get":
            return self._handle_get(tokens[1:])
        elif cmd == "help":
            return self._help()
        else:
            return f"Unknown command: {cmd}"

    def _handle_set(self, args):
        name = args[0]
        values = args[1:]

        if name not in self.schema:
            return f"Unknown setting '{name}'"

        cfg = self.schema[name]

        if cfg["type"] == "vector3":
            return self._set_vector3(name, cfg, values)

        if cfg["type"] == "int":
            return self._set_int(name, cfg, values)

        return "Unsupported type"

    def _set_vector3(self, name, cfg, values):
        if len(values) != 3:
            return "Expected 3 values (X Y Z)"

        axes = ["X", "Y", "Z"]
        for axis, raw in zip(axes, values):
            val = float(raw)
            if val > cfg["max"]:
                return f"{axis} exceeds max {cfg['max']}"

            plc_key = cfg["plc_map"][axis]
            self.plc.write(plc_key, val)

        return f"{name} set successfully"

    def _set_int(self, name, cfg, values):
        if len(values) != 1:
            return "Expected single integer value"

        val = int(values[0])
        if not (cfg["min"] <= val <= cfg["max"]):
            return f"Value out of range ({cfg['min']}–{cfg['max']})"

        self.plc.write(cfg["plc"], val)
        return f"{name} set to {val}"

    def _handle_get(self, args):
        name = args[0]
        cfg = self.schema.get(name)
        if not cfg:
            return "Unknown setting"

        if cfg["type"] == "vector3":
            return {
                axis: self.plc.read(plc_key)
                for axis, plc_key in cfg["plc_map"].items()
            }

        return self.plc.read(cfg["plc"])

    def _help(self):
        return f"Available settings: {', '.join(self.schema.keys())}"

def toggle_operation_mode(app):
    app.operationSwitch = app.operation_mode_var.get()
    set_bit("Power_Python", app.operationSwitch)


def create_settings_widgets(app):
    """
    Create the settings screen widgets.
    :param app:
    """

    # Make frame for settings
    settingsFrame = ctk.CTkFrame(app.contentFrame)
    settingsFrame.pack(fill='both', padx=20, pady=20)

    settingsLabel = ctk.CTkLabel(settingsFrame, text="Settings Screen",
                                 font=ctk.CTkFont(size=20, weight="bold"))
    settingsLabel.pack(pady=20)

    # Make switch to enable operation mode
    app.switch = ctk.CTkSwitch(
        settingsFrame,
        text="Enable operation Mode",
        variable=app.operation_mode_var,
        onvalue=True,
        offvalue=False,
        command=lambda: toggle_operation_mode(app)
    )
    app.switch.pack(pady=10)

    settingsOptions = ctk.CTkOptionMenu(settingsFrame, values=settingsScreenButtons)
    settingsOptions.pack(pady=10)
    settingsOptions.set("Select setting to configure")

    app.settingsSelectButton = ctk.CTkButton(settingsFrame,
                                             text="Select",
                                             command=lambda: select_setting(app, settingsFrame,settingsOptions.get()))
    app.settingsSelectButton.pack(pady=5)
    # app.settings_engine = SettingsEngine(
    #     "Python_code/settings_schema.json",
    # )
    # terminal_frame = ctk.CTkFrame(settingsFrame)
    # terminal_frame.pack(fill="x", pady=15)
    #
    # terminal_label = ctk.CTkLabel(
    #     terminal_frame, text="Command terminal"
    # )
    # terminal_label.pack(anchor="w")
    #
    # app.terminal_entry = ctk.CTkEntry(
    #     terminal_frame,
    #     placeholder_text="set speed 100 120 80"
    # )
    # app.terminal_entry.pack(fill="x", pady=5)
    #
    # app.terminal_output = ctk.CTkTextbox(
    #     terminal_frame, height=120
    # )
    # app.terminal_output.pack(fill="x")

    # def run_terminal_command():
    #     cmd = app.terminal_entry.get()
    #     result = app.settings_engine.execute(cmd)
    #     app.terminal_output.insert("end", f"> {cmd}\n{result}\n\n")
    #     app.terminal_entry.delete(0, "end")
    #
    # terminal_btn = ctk.CTkButton(
    #     terminal_frame,
    #     text="Execute",
    #     command=run_terminal_command
    # )
    # terminal_btn.pack(pady=5)


def select_setting(app, frame, selected_option):
    """
    Create widgets for the selected setting option.
    :param app: Instance of the main application
    :param frame: Frame to place the widgets in
    :param selected_option: The selected setting option
    """

    # Make settingsFrame global to access it
    settingsFrame = frame

    # Check if the frame already exists and destroy it
    if hasattr(app, 'optionWidgetFrame') and app.optionWidgetFrame is not None:
        app.optionWidgetFrame.destroy()

    # Create a new frame for the selected option's widgets
    app.optionWidgetFrame = ctk.CTkFrame(settingsFrame)
    app.optionWidgetFrame.pack(fill='both', expand=True, padx=20, pady=20)

    # Clear previous widgets
    for widget in app.optionWidgetFrame.winfo_children():
        widget.destroy()

    build_option_widgets(app, selected_option)


def build_option_widgets(app, selected_option):
    # Clear old widgets
    for widget in app.optionWidgetFrame.winfo_children():
        widget.destroy()

    app.input_entries = {}
    config = setting_widgets[selected_option]

    frame = ctk.CTkFrame(app.optionWidgetFrame, fg_color="transparent")
    frame.pack(pady=5)

    # Build entries
    for idx, (entry_name, placeholder) in enumerate(config["entries"]):

        entry = ctk.CTkEntry(frame, placeholder_text=placeholder)

        if config["use_grid"]:
            entry.grid(row=0, column=idx, padx=5, pady=5)
        else:
            entry.pack(pady=5)

        app.input_entries[entry_name] = entry

    # Button
    button = ctk.CTkButton(
        frame if config["use_grid"] else app.optionWidgetFrame,
        text=config["button_text"],
        command=lambda: choose_function(app, selected_option)
    )

    if config["use_grid"]:
        button.grid(row=1, column=len(config["entries"]) // 2, pady=10)
    else:
        button.pack(pady=5)


def choose_function(app, selected_option):
    """
    Choose and call the appropriate function based on the selected option.
    :param app: main application instance
    :param selected_option: The selected setting option
    """
    functions = {
        "Speed": set_speed_from_entry,
        "Acceleration": set_acceleration_from_entry,
        "Cycles": set_cycles_from_entry,
        "Pallets": set_pallets_from_entry,
        "Pick coordinates": set_pick_coordinates_from_entry,
        "Place coordinates": set_place_coordinates_from_entry,
    }

    func = functions.get(selected_option, None)

    if func:
        func(app)
    else:
        write_log(f"No function defined for {selected_option}")


def check_speed_values(app, speedX, speedY, speedZ):
    """
    Check and validate speed values from the entries.
    :param app: main application instance
    :param speedX: raw input for X axis speed
    :param speedY: raw input for Y axis speed
    :param speedZ: raw input for Z axis speed
    :return: tuple (valid_values_dict, errors_dict)
    """
    # Define variables
    max_speed = MAX_SPEED_DEG_PER_S
    results = {}
    errors = {}

    def validate(value, axis, entry_name):
        """
        Validate a single speed value.
        :param value: value as entered by the user
        :param axis: which axis ('X', 'Y', or 'Z')
        :param entry_name: name of the entry widget
        :return: Validated float value or None
        """
        entry = app.input_entries[entry_name]

        # Check if value is a number
        try:
            val = float(value)
        except ValueError:
            # Value is not a number inform the user
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, "Enter a number")

            errors[axis] = "invalid"
            return False

        # Check if value exceeds max speed
        if val > max_speed:
            # Value too high, inform the user
            entry.configure(fg_color="#8B0000",
                            placeholder_text=f"Max speed is {max_speed}")
            entry.delete(0, "end")
            entry.insert(0, f"Max speed is {max_speed}")

            errors[axis] = "too_high"
            return False

        # Value is valid
        entry.configure(fg_color="green")
        results[axis] = val
        return True

    # Call validate for each axis
    validate(speedX, "X", "speedEntryX")
    validate(speedY, "Y", "speedEntryY")
    validate(speedZ, "Z", "speedEntryZ")

    return results, errors


def set_speed_from_entry(app):
    """
    Set speed values from the entry fields.
    :param app: main application instance
    """
    valid, errors = check_speed_values(app,
                                       app.input_entries["speedEntryX"].get(),
                                       app.input_entries["speedEntryY"].get(),
                                       app.input_entries["speedEntryZ"].get()
                                       )
    # Write log if no valid values
    if not valid:
        write_log("No valid speed values.")
        return
    # To control widgets
    AXES = {
        "X": "speedEntryX",
        "Y": "speedEntryY",
        "Z": "speedEntryZ",
    }
    # For each axis, write value to PLC
    for axis, value in valid.items():
        entry = app.input_entries[AXES[axis]]

        # Write to PLC
        try:
            write_lreal(LREAL_OFFSETS[f"{axis}_Speed_Python"], value)

            # Check if PLC got the value
            if read_lreal(LREAL_OFFSETS[f"{axis}_Speed_Python"]) == value:
                write_log(f"Speed {axis} set to {value}")
                # Indicate success
                entry.configure(fg_color="green")

            # If not confirmed by PLC inform the user
            else:
                write_log(f"Speed {axis} not confirmed by PLC")
                entry.configure(fg_color="#8B0000")
                entry.delete(0, "end")
                entry.insert(0, "PLC no response")

        # Handle unexpected errors
        except Exception as e:
            write_log(f"PLC error on {axis}: {e}")
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, f" {axis} error: {e}")

    # Log errors for invalid entries
    for axis, reason in errors.items():
        write_log(f"Speed {axis} {reason}.")


def check_accel_values(app, accelX, accelY, accelZ):
    """
    Check and validate acceleration values from the entries.
    :param app: main application instance
    :param accelX: raw input for X axis acceleration
    :param accelY: raw input for Y axis acceleration
    :param accelZ: raw input for Z axis acceleration
    :return: tuple (valid_values_dict, errors_dict)
    """
    # Define variables
    max_accel = MAX_ACCEL_DEG_PER_S2
    results = {}
    errors = {}

    def validate(value, axis, entry_name):
        """
        Validate a single acceleration value.
        :param value: value as entered by the user
        :param axis: which axis ('X', 'Y', or 'Z')
        :param entry_name: name of the entry widget
        :return: Validated float value or None
        """
        entry = app.input_entries[entry_name]

        # Check if value is a number
        try:
            val = float(value)
        except ValueError:
            # Value is not a number inform the user
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, "Enter a number")

            errors[axis] = "invalid"
            return False

        # Check if value exceeds max acceleration
        if val > max_accel:
            # Value too high, inform the user
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, f"Max accel is {max_accel}")

            errors[axis] = "too_high"
            return False

        # Value is valid
        entry.configure(fg_color="green")
        results[axis] = val
        return val

    # Call validate for each axis
    validate(accelX, "X", "accelEntryX")
    validate(accelY, "Y", "accelEntryY")
    validate(accelZ, "Z", "accelEntryZ")

    return results, errors


def set_acceleration_from_entry(app):
    """
    Set acceleration values from the entry fields.
    :param app: main application instance
    """
    valid, errors = check_accel_values(app,
                                       app.input_entries["accelEntryX"].get(),
                                       app.input_entries["accelEntryY"].get(),
                                       app.input_entries["accelEntryZ"].get()
                                       )
    # Write log if no valid values
    if not valid:
        write_log("No valid acceleration values.")
        return
    # To control widgets
    AXES = {
        "X": "accelEntryX",
        "Y": "accelEntryY",
        "Z": "accelEntryZ",
    }
    # For each axis, write value to PLC
    for axis, value in valid.items():
        entry = app.input_entries[AXES[axis]]

        # Write to PLC
        try:
            write_lreal(LREAL_OFFSETS[f"{axis}_Acceleration_Python"], value)

            # Check if PLC got the value
            if read_lreal(LREAL_OFFSETS[f"{axis}_Acceleration_Python"]) == value:
                write_log(f"Acceleration {axis} set to {value}")
                # Indicate success
                entry.configure(fg_color="green")

            # If not confirmed by PLC inform the user
            else:
                write_log(f"Acceleration {axis} not received")
                entry.configure(fg_color="#8B0000")
                entry.delete(0, "end")
                entry.insert(0, "PLC no response")

        # Handle unexpected errors
        except Exception as e:
            write_log(f"Error writing acceleration {axis}: {e}")
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, f" {axis} error: {e}")

    # Log errors for invalid entries
    for axis, reason in errors.items():
        write_log(f"Acceleration {axis} {reason}.")


def check_cycles_value(app, value):
    """
    Check and validate cycles value from the entry.
    :param app: main application instance
    :param value: User input for number of cycles
    :return: True if valid, False otherwise
    """
    entry = app.input_entries["cyclesEntry"]

    # Check if value is a number
    try:
        val = int(value)
    except ValueError:
        # Value is not a number inform the user
        entry.configure(fg_color="#8B0000")
        entry.delete(0, "end")
        entry.insert(0, "Enter a number")

        return False

    # Check if value exceeds max cycles
    if val < 1 or val > MAX_CYCLES:
        # Value too high, inform the user
        entry.configure(fg_color="#8B0000")
        entry.delete(0, "end")
        entry.insert(0, f"Max cycles is {MAX_CYCLES}")

        return False

    # Value is valid
    entry.configure(fg_color="green")
    return True


def set_cycles_from_entry(app):
    """
    Set cycles value from the entry field.
    :param app: main application instance
    """

    entry = app.input_entries["cyclesEntry"]
    cycles = app.input_entries["cyclesEntry"].get()
    valid = check_cycles_value(app, cycles)

    # Write log if not valid
    if not valid:
        write_log(f"Invalid cycles value. {cycles}")
        return
    app.value = app.input_entries["cyclesEntry"].get()
    # Write to PLC
    try:
        write_int(INT_OFFSETS["Cycles_Python"], cycles)

        # Check if PLC got the value
        if read_int(INT_OFFSETS["Cycles_Python"]) == cycles:
            write_log(f"Cycles set to {cycles}")
            entry.configure(fg_color="green")

        # If not confirmed by PLC inform the user
        else:
            write_log("Cycle value not confirmed, check connection PLC")
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, "Cycle value not confirmed, check connection PLC")

    # Handle unexpected errors
    except Exception as e:
        write_log(f"Error writing cycles: {e}")
        entry.configure(fg_color="#8B0000")
        entry.delete(0, "end")
        entry.insert(0, f"Error writing cycles: {e}")


def check_pallet_value(app, pallets):
    """
    Check and validate pallets value from the entry.
    :param app: main application instance
    :param pallets: raw input for number of pallets
    :return: True if valid, False otherwise
    """
    entry = app.input_entries["palletsEntry"]

    # Check if value is a number
    try:
        val = int(pallets)
    except ValueError:
        # Value is not a number inform the user
        entry.configure(fg_color="#8B0000")
        entry.delete(0, "end")
        entry.insert(0, "Enter a number")
        return False

    # Check if value exceeds max pallets
    if val < 1 or val > MAX_PALLETS:
        # Value too high, inform the user
        entry.configure(fg_color="#8B0000")
        entry.delete(0, "end")
        entry.insert(0, f"Max pallets is {MAX_PALLETS}")

        return False

    # Value is valid
    entry.configure(fg_color="green")
    return True


def set_pallets_from_entry(app):
    """
    Set pallets value from the entry field.
    :param app: main application instance
    """
    entry = app.input_entries["palletsEntry"]
    pallets = app.input_entries["palletsEntry"].get()
    valid = check_pallet_value(app, pallets)

    # Write log if not valid
    if not valid:
        write_log(f"Invalid pallets value.{pallets}")
        return

    # Write to PLC
    try:
        write_int(INT_OFFSETS["Pallets_Python"], pallets)

        # Check if PLC got the value
        if read_int(INT_OFFSETS["Pallets_Python"]) == pallets:
            write_log(f"Pallets set to {pallets}")
            entry.configure(fg_color="green")

        # If not confirmed by PLC inform the user
        else:
            write_log("Pallets value not received")
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, "Pallets value not received")

    # Handle unexpected errors
    except Exception as e:
        write_log(f"Error writing pallets: {e}")
        entry.configure(fg_color="#8B0000")
        entry.delete(0, "end")
        entry.insert(0, f"Error writing pallets: {e}")


def check_coordinates(app, x, y, z):
    """
    Check and validate coordinate values.
    :param x: X coordinate
    :param y: Y coordinate
    :param z: Z coordinate
    :return: True if valid, False otherwise
    """
    max_coord_x = MAX_COORD_X
    max_coord_y = MAX_COORD_Y
    max_coord_z = MAX_COORD_Z
    results = {}
    errors = {}

    def validate(app, value, axis, entry_name):
        """
        Validate a single coordinate value.
        :param app: main gui instance
        :param value: value as entered by the user
        :param axis: which axis ('X', 'Y', or 'Z')
        :param entry_name: name of the entry widget
        :return: Validated float value or None
        """
        entry = app.input_entries[entry_name]

        # Check if value is a number
        try:
            val = float(value)
        except ValueError:
            # Value is not a number inform the user
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, "Enter a number")

            errors[axis] = "invalid"
            return False

        # Check if value exceeds max coordinate
        if (axis == "X" and abs(val) > max_coord_x) or \
           (axis == "Y" and abs(val) > max_coord_y) or \
           (axis == "Z" and abs(val) > max_coord_z):
            # Value too high, inform the user
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, f"Max {axis} is {max_coord_x if axis == 'X' else max_coord_y if axis == 'Y' else max_coord_z}")

            errors[axis] = "too_high"
            return False

        # Value is valid
        entry.configure(fg_color="green")
        results[axis] = val
        return True

    # Call validate for each axis
    validate(app, x, "X", "pickXEntry")
    validate(app, y, "Y", "pickYEntry")
    validate(app, z, "Z", "pickZEntry")

    return results, errors


def set_pick_coordinates_from_entry(app):

    valid = check_coordinates(app.pickXEntry.get(), app.pickYEntry.get(), app.pickZEntry.get())

    if not valid:
        write_log("Invalid pick coordinates.")
        return

    for axis in valid.items():
        entry = app.input_entries[f"pick{axis}Entry"]
        value = app.input_entries[f"pick{axis}Entry"].get()

    try:
        write_lreal(LREAL_OFFSETS[f"Pick_{axis}_Python"], value)

        if write_lreal(LREAL_OFFSETS[f"Pick_{axis}_Python"]) == value:
            write_log(f"Pick {axis} coordinate set to {value}")
            entry.configure(fg_color="green")

        else:
            write_log(f"Pick {axis} coordinate not confirmed by PLC")
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, "PLC no response")

    except Exception as e:
        write_log("Error writing pick coordinates: {e}")
        entry.configure(fg_color="#8B0000")
        entry.delete(0, "end")
        entry.insert(0, f"Error writing pick coordinates: {e}")


def set_place_coordinates_from_entry(app):
    valid = check_coordinates(app,
                              app.placeXEntry.get(),
                              app.placeYEntry.get(),
                              app.placeZEntry.get()
                              )

    if not valid:
        write_log("Invalid place coordinates.")
        return

    for axis in valid.items():
        entry = app.input_entries[f"place{axis}Entry"]
        value = app.input_entries[f"place{axis}Entry"].get()

    try:
        write_int(INT_OFFSETS[f"Place_{axis}_Python"], value)

        if read_int(INT_OFFSETS[f"Place_{axis}_Python"]) == value:
            write_log(f"Place {axis} coordinate set to {value}")
            entry.configure(fg_color="green")

        else:
            write_log(f"Place {axis} coordinate not confirmed by PLC")
            entry.configure(fg_color="#8B0000")
            entry.delete(0, "end")
            entry.insert(0, "PLC no response")

    except Exception as e:
        write_log("Error writing place coordinates: {e}")
        entry.configure(fg_color="#8B0000")
        entry.delete(0, "end")
        entry.insert(0, f"Error writing place coordinates: {e}")