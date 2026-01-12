# control_screen.py

# Imports from python libs
import customtkinter as ctk
import math
import struct
import tkinter as tk
from tkinter import messagebox

# Imports within the project
from Python_code.Logger.logger import *  # Functions to log events in the GUI
from Python_code.Communication.communicationTia import *  # Functions to communicate with a PLC
from Python_code.Communication.communicationConfig import *


def create_control_widgets(app):
    """
    Create the control screen widgets.
    :param app: instance of the main application
    """

    # Make frame for joystick controls
    joystickFrame = ctk.CTkFrame(app.contentFrame, corner_radius=12)
    joystickFrame.pack(fill="both", expand=True, padx=12, pady=12)
    joystickLabel = ctk.CTkLabel(joystickFrame, text="Live Joystick %")
    joystickLabel.pack(anchor="n", pady=(8, 4))

    # Make frame for displaying joystick percentage values
    valuesFrame = ctk.CTkFrame(joystickFrame, fg_color="transparent")
    valuesFrame.pack(pady=(0, 8))

    # Labels for X, Y, Z percentages
    ctk.CTkLabel(valuesFrame, text="X:").grid(row=0, column=0, padx=5)
    ctk.CTkLabel(valuesFrame, textvariable=app.pct_x).grid(row=0, column=1, padx=5)
    ctk.CTkLabel(valuesFrame, text="Y:").grid(row=0, column=2, padx=5)
    ctk.CTkLabel(valuesFrame, textvariable=app.pct_y).grid(row=0, column=3, padx=5)
    ctk.CTkLabel(valuesFrame, text="Z:").grid(row=0, column=4, padx=5)
    ctk.CTkLabel(valuesFrame, textvariable=app.pct_z).grid(row=0, column=5, padx=5)

    # Create left and right frames for joysticks
    joy_left = ctk.CTkFrame(joystickFrame, corner_radius=12)
    joy_right = ctk.CTkFrame(joystickFrame, corner_radius=12)
    joy_left.pack(side="left")
    joy_right.pack(side="right")

    # Create Joystick widgets
    app.jxy = Joystick(joy_left, label="Joystick X/Y",
                       diameter=240, on_change=lambda x, y: on_xy(app, x, y))
    app.jxy.pack(padx=12, pady=12)

    app.jz = Joystick(joy_right, label="Joystick Z",
                      diameter=240, only_vertical=True, on_change=lambda _x, y: on_z(app, _x, y))
    app.jz.pack(padx=12, pady=12)


def scaled_percent(app, axis_val: float) -> float:
    """
    Convert joystick axis value (-1..1) to scaled percentage (0..100) considering deadzone.
    :param app: instance of the main application
    :param axis_val: Axis value from joystick (-1.0 to +1.0)
    :return: Scaled percentage (0.0 to 100.0)
    """
    dz = float(app.deadzone.get())
    a = abs(axis_val)
    if a <= dz:
        return 0.0
    pct = (a - dz) / max(1e-6, (1.0 - dz))
    pct = max(0.0, min(1.0, pct))
    return pct * 100.0


def speed_signed(app, axis_val: float) -> float:
    """
    Convert joystick axis value (-1..1) to speed in degrees per second (-MAX..+MAX).
    """
    percent = scaled_percent(app, axis_val)  # 0..100
    mag = (percent / 100.0) * MAX_SPEED_DEG_PER_S
    spd = math.copysign(mag, axis_val)
    return max(-MAX_SPEED_DEG_PER_S, min(MAX_SPEED_DEG_PER_S, round(spd, 1)))


def write_speed_if_changed(app, name: str, value: float):
    """
    Write speed to PLC if it has changed.
    :param app: instance of the main application
    :param name: name of the speed variable
    :param value: value to write
    :return:
    """
    last = app.last_speed.get(name)
    if last is None or abs(value - last) >= 0.1:
        try:
            write_lreal(LREAL_OFFSETS[name], value)
            app.last_speed[name] = value
            ent = app.lreal_entries.get(name)

            if ent is not None:
                ent.delete(0, "end")
                ent.insert(0, f"{value: .1f}")

        except Exception as e:
            write_log(f"Error writing speed {name}: {e}")


def apply_bits(app, desired: dict):
    """
    Apply desired bit states to the PLC if they have changed.
    This is used for the joystick direction bits.
    :param app: instance of the main application
    :param desired: dict of bit names and desired states
    """
    for name, state in desired.items():
        if app.last_state.get(name) != state:
            try:
                set_bit(BITS_ALL[name], state)
                app.last_state[name] = state
            except Exception as e:
                write_log(f"Error writing bit {name}: {e}")


def handle_axis(app, axis: str, val: float, fwd_bit: str, bwd_bit: str, speed_name: str):
    """
    Handle joystick axis input and update PLC bits and speed accordingly.
    :param app: instance of the main application
    :param axis: Axis name ("X", "Y", or "Z")
    :param val: Axis value (-1.0 to +1.0)
    :param fwd_bit: Name of the forward direction bit
    :param bwd_bit: Name of the backward direction bit
    :param speed_name: Name of the speed variable
    """
    th = float(app.threshold.get())

    # Speed
    spd = speed_signed(app, val)
    write_speed_if_changed(app, speed_name, spd)

    # Direction bits
    sign_bits = 1 if val > th else (-1 if val < -th else 0)
    last_bits = app.axis_last_bits_sign[axis]

    if sign_bits != last_bits:
        if sign_bits == 1:
            apply_bits(app, {fwd_bit: True, bwd_bit: False})
        elif sign_bits == -1:
            apply_bits(app, {fwd_bit: False, bwd_bit: True})
        else:
            apply_bits(app, {fwd_bit: False, bwd_bit: False})
            write_speed_if_changed(app, speed_name, 0.0)
        app.axis_last_bits_sign[axis] = sign_bits

    # Update percentage display
    percent = abs(scaled_percent(app, val))
    if axis == "X":
        app.pct_x.set(f"{percent: .0f}%")
    elif axis == "Y":
        app.pct_y.set(f"{percent: .0f}%")
    elif axis == "Z":
        app.pct_z.set(f"{percent: .0f}%")


def on_xy(app, x, y):
    """
    Handle X and Y joystick input.
    :param app: Instance of the main application
    :param x: X axis value of the joystick
    :param y: Y axis value of the joystick
    """
    handle_axis(app, "X", x, "Forward_X_Python", "Backward_X_Python", "Joystick_X_speed")
    handle_axis(app, "Y", y, "Forward_Y_Python", "Backward_Y_Python", "Joystick_Y_speed")


def on_z(app, _x, y):
    """
    Handle Z joystick input.
    :param app: Instance of the main application
    :param _x: X axis value of the joystick always the same
    :param y: Y axis value of the joystick
    :return:
    """
    handle_axis(app, "Z", y, "Forward_Z_Python", "Backward_Z_Python", "Joystick_Z_speed")


"""
Honestly no clue how the code below works
DONT DEAD OPEN INSIDE!
"""


class Indicator(ctk.CTkFrame):
    """
    An indicator light with label.
    :param master: Parent widget
    """
    def __init__(self, master, text: str, color_on: str, diameter: int = 14):
        super().__init__(master, fg_color="transparent")
        self.color_on = color_on
        self.canvas = tk.Canvas(self, width=diameter, height=diameter,
                                highlightthickness=0, bg="#2b2b2b")
        self.dot = self.canvas.create_oval(2, 2, diameter-2, diameter-2,
                                           fill="#555555", outline="#222222", width=1)
        self.canvas.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(self, text=text).pack(side="left")

    def set(self, on: bool):
        self.canvas.itemconfig(self.dot, fill=(self.color_on if on else "#555555"))


class Joystick(ctk.CTkFrame):
    """
    A Joystick widget for 2D input.
    :param master: Parent widget
    """
    def __init__(self, master, label="", diameter=240, only_vertical=False, on_change=None):
        super().__init__(master, corner_radius=12)
        self.on_change = on_change
        self.only_vertical = only_vertical
        self.d = diameter
        self.r = diameter // 2
        self.knob_r = max(18, int(self.r * 0.33))

        if label:
            ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(8, 0))

        self.canvas = tk.Canvas(self, width=self.d, height=self.d, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)

        self.canvas.create_oval(4, 4, self.d - 4, self.d - 4, outline="#4a4a4a", width=2)
        self.canvas.create_line(self.r, 8, self.r, self.d - 8, fill="#3e3e3e")
        self.canvas.create_line(8, self.r, self.d - 8, self.r, fill="#3e3e3e")

        self.knob = self.canvas.create_oval(self.r - self.knob_r, self.r - self.knob_r,
                                            self.r + self.knob_r, self.r + self.knob_r,
                                            fill="#1f6aa5", outline="#0f3c60", width=2)

        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.release)

    def center(self):
        self.set_knob(self.r, self.r)
        if self.on_change:
            self.on_change(0.0, 0.0)

    def set_knob(self, cx, cy):
        r = self.knob_r
        self.canvas.coords(self.knob, cx - r, cy - r, cx + r, cy + r)

    def process(self, x, y):
        vx, vy = x - self.r, y - self.r
        if self.only_vertical:
            vx = 0
        max_radius = self.r - self.knob_r - 4
        dist = math.hypot(vx, vy)
        if dist > max_radius and dist != 0:
            scale = max_radius / dist
            vx *= scale
            vy *= scale
        cx, cy = int(self.r + vx), int(self.r + vy)
        self.set_knob(cx, cy)
        nx = vx / max_radius
        ny = -vy / max_radius
        if self.on_change:
            self.on_change(nx, ny)

    def click(self, e):   self.process(e.x, e.y)
    def drag(self, e):    self.process(e.x, e.y)
    def release(self, _): self.center()
