# control_screen.py

# Imports from python libs
import customtkinter as ctk
import math
import tkinter as tk
import cv2
import threading
from PIL import Image, ImageTk

# Imports within the project
from Python_code.Logger.logger import *
from Python_code.Communication.communicationTia import *
from Python_code.Communication.communicationConfig import *


def create_control_widgets(app):
    """
    Create the control screen widgets.
    """

    # =========================
    # Main layout frame (3 columns)
    # =========================
    mainFrame = ctk.CTkFrame(app.contentFrame, corner_radius=12)
    mainFrame.pack(fill="both", expand=True, padx=12, pady=12)

    mainFrame.columnconfigure((0, 1, 2), weight=1)
    mainFrame.rowconfigure(0, weight=0)

    # =========================
    # Joystick percentage display (top, spans all)
    # =========================
    infoFrame = ctk.CTkFrame(mainFrame)
    infoFrame.grid(row=0, column=0, columnspan=3, pady=(4, 8))

    # =========================
    # Left / Center / Right
    # =========================
    leftFrame = ctk.CTkFrame(mainFrame, corner_radius=12)
    centerFrame = ctk.CTkFrame(mainFrame, corner_radius=12)
    rightFrame = ctk.CTkFrame(mainFrame, corner_radius=12)

    leftFrame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
    centerFrame.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
    rightFrame.grid(row=1, column=2, sticky="nsew", padx=8, pady=8)

    ctk.CTkLabel(infoFrame, text="X:").grid(row=0, column=0, padx=5)
    ctk.CTkLabel(infoFrame, textvariable=app.pct_x).grid(row=0, column=1, padx=5)
    ctk.CTkLabel(infoFrame, text="Y:").grid(row=0, column=2, padx=5)
    ctk.CTkLabel(infoFrame, textvariable=app.pct_y).grid(row=0, column=3, padx=5)
    ctk.CTkLabel(infoFrame, text="Z:").grid(row=0, column=4, padx=5)
    ctk.CTkLabel(infoFrame, textvariable=app.pct_z).grid(row=0, column=5, padx=5)
    ctk.CTkLabel(infoFrame, text="R:").grid(row=0, column=6, padx=5)
    ctk.CTkLabel(infoFrame, textvariable=app.pct_r).grid(row=0, column=7, padx=5)

    # =========================
    # Left joystick (X/Y)
    # =========================
    app.jxy = Joystick(
        leftFrame,
        label="Joystick X / Y",
        diameter=240,
        on_change=lambda x, y: on_xy(app, x, y)
    )
    app.jxy.pack(expand=True, pady=12)

    # =========================
    # Right joystick (Z)
    # =========================
    app.jz = Joystick(
        rightFrame,
        label="Joystick Z",
        diameter=240,
        only_vertical=True,
        on_change=lambda _x, y: on_z(app, _x, y)
    )
    app.jz.pack(expand=True, pady=12)

    app.rotation = RotationKnob(
        rightFrame,
        label="Rotation",
        diameter=200,
        max_angle=180,
        on_change=lambda r: on_rotation(app, r)
    )
    app.rotation.pack(pady=12)

    # =========================
    # CENTER: Camera view
    # =========================
    ctk.CTkLabel(
        centerFrame,
        text="LIVE CAMERA",
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(pady=(12, 6))

    app.cameraCanvas = tk.Canvas(
        centerFrame,
        width=1080,
        height=720,
        bg="black",
        highlightthickness=0
    )
    app.cameraCanvas.pack(expand=True, padx=12, pady=12)
    app.cross_v = app.cameraCanvas.create_line(0, 0, 0, 0, fill="gray")
    app.cross_h = app.cameraCanvas.create_line(0, 0, 0, 0, fill="gray")

    app.camera_image_id = app.cameraCanvas.create_image(
        0, 0, anchor="nw"
    )
    app.magnet_btn = ctk.CTkButton(
        mainFrame,
        text="MAGNEET AAN",
        fg_color="green",
        hover_color="#555555",
        height=48,
        font=ctk.CTkFont(size=16, weight="bold"),
        command=lambda: toggle_magnet(app)
    )

    app.magnet_btn.grid(row=3, column=1)

    def update_canvas():
        if app.latest_frame is not None:
            frame = app.latest_frame

            cw = app.cameraCanvas.winfo_width()
            ch = app.cameraCanvas.winfo_height()

            if cw > 1 and ch > 1:
                cx = cw // 2
                cy = ch // 2

                app.cameraCanvas.coords(app.cross_v, cx, 0, cx, ch)
                app.cameraCanvas.coords(app.cross_h, 0, cy, cw, cy)

                frame = cv2.resize(frame, (cw, ch), interpolation=cv2.INTER_LINEAR)

            img = Image.fromarray(frame)
            app.camera_image = ImageTk.PhotoImage(img)

            app.cameraCanvas.itemconfig(
                app.camera_image_id,
                image=app.camera_image
            )

        app.cameraCanvas.tag_raise(app.cross_v)
        app.cameraCanvas.tag_raise(app.cross_h)

        # 30 FPS ≈ 33 ms
        app.cameraCanvas.after(33, update_canvas)

    update_canvas()


# ==========================================================
# Logic
# ==========================================================
def scaled_percent(app, axis_val: float) -> float:
    dz = float(app.deadzone.get())
    a = abs(axis_val)
    if a <= dz:
        return 0.0
    pct = (a - dz) / max(1e-6, (1.0 - dz))
    return max(0.0, min(1.0, pct)) * 100.0


def write_speed_if_changed(app, name: str, value: float):
    last = app.last_speed.get(name)
    if last is None or abs(value - last) >= 0.1:
        try:
            write_lreal(name, value)
            app.last_speed[name] = value
        except Exception as e:
            write_log(f"Error writing speed {name}: {e}")


def apply_bits(app, desired: dict):
    for name, state in desired.items():
        try:
            set_bit(name, state)
        except Exception as e:
            write_log(f"Error writing bit {name}: {e}")


def signed_percent(app, axis_val: float) -> float:
    dz = float(app.deadzone.get())
    a = abs(axis_val)

    if a <= dz:
        return 0.0

    pct = (a - dz) / max(1e-6, (1.0 - dz))
    pct = max(0.0, min(1.0, pct)) * 100.0

    return pct if axis_val > 0 else -pct


def handle_axis(app, axis: str, val: float, fwd_bit: str, bwd_bit: str, speed_name: str):
    th = float(app.threshold.get())

    if val > th:
        direction = 1
    elif val < -th:
        direction = -1
    else:
        direction = 0

    signed_pct = signed_percent(app, val)
    speed = abs(signed_pct)

    write_speed_if_changed(app, speed_name, speed)

    if direction == 1:
        apply_bits(app, {fwd_bit: True, bwd_bit: False})
    elif direction == -1:
        apply_bits(app, {fwd_bit: False, bwd_bit: True})
    else:
        apply_bits(app, {fwd_bit: False, bwd_bit: False})

    pct = speed
    if axis == "X":
        app.pct_x.set(f"{signed_pct:+.0f}%")
    elif axis == "Y":
        app.pct_y.set(f"{signed_pct:+.0f}%")
    elif axis == "Z":
        app.pct_z.set(f"{signed_pct:+.0f}%")


def on_xy(app, x, y):
    handle_axis(app, "X", x, "Forward_X_Python", "Backward_X_Python", "Joystick_X_speed")
    handle_axis(app, "Y", y, "Forward_Y_Python", "Backward_Y_Python", "Joystick_Y_speed")


def on_z(app, _x, y):
    handle_axis(app, "Z", y, "Forward_Z_Python", "Backward_Z_Python", "Joystick_Z_speed")


def on_rotation(app, value):
    write_log(f"Rotation value: {value}")
    deg = value * 180
    app.pct_r.set(f"{deg:+.0f}°")
    handle_axis(app, "R", value, "Forward_R_Python", "Backward_R_Python", "Joystick_R_speed")


# ==========================================================
# Widgets
# ==========================================================

class Joystick(ctk.CTkFrame):
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

        self.knob = self.canvas.create_oval(
            self.r - self.knob_r, self.r - self.knob_r,
            self.r + self.knob_r, self.r + self.knob_r,
            fill="#1f6aa5", outline="#0f3c60", width=2
        )

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

    def click(self, e): self.process(e.x, e.y)
    def drag(self, e): self.process(e.x, e.y)
    def release(self, _): self.center()


class RotationKnob(ctk.CTkFrame):
    def __init__(
        self,
        master,
        label="Rotation",
        diameter=200,
        max_angle=180,
        on_change=None
    ):
        super().__init__(master, corner_radius=12)

        self.on_change = on_change
        self.d = diameter
        self.r = diameter // 2
        self.max_angle = max_angle
        self.angle = 0.0

        if label:
            ctk.CTkLabel(
                self,
                text=label,
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(pady=(8, 0))

        self.canvas = tk.Canvas(
            self,
            width=self.d,
            height=self.d,
            bg="#2b2b2b",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)

        # Outer circle
        self.canvas.create_oval(
            4, 4, self.d - 4, self.d - 4,
            outline="#4a4a4a", width=2
        )

        # Center
        self.canvas.create_oval(
            self.r - 4, self.r - 4,
            self.r + 4, self.r + 4,
            fill="#888", outline=""
        )

        # Pointer
        self.pointer = self.canvas.create_line(
            self.r, self.r,
            self.r, 10,
            fill="#1f6aa5",
            width=4
        )

        self.canvas.bind("<Button-1>", self.update_angle)
        self.canvas.bind("<B1-Motion>", self.update_angle)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

    def update_angle(self, e):
        dx = e.x - self.r
        dy = self.r - e.y

        angle = math.degrees(math.atan2(dx, dy))
        angle = max(-self.max_angle, min(self.max_angle, angle))
        self.angle = angle

        rad = math.radians(angle)
        x = self.r + math.sin(rad) * (self.r - 10)
        y = self.r - math.cos(rad) * (self.r - 10)

        self.canvas.coords(self.pointer, self.r, self.r, x, y)

        if self.on_change:
            self.on_change(angle / self.max_angle)

    def reset(self, _):
        self.angle = 0.0
        self.canvas.coords(self.pointer, self.r, self.r, self.r, 10)
        if self.on_change:
            self.on_change(0.0)

def toggle_magnet(app):
    app.magnet_on = not app.magnet_on

    try:
        set_bit("Magneet_Python", app.magnet_on)
    except Exception as e:
        write_log(f"Error toggling magnet: {e}")
        return

    # UI feedback
    if not app.magnet_on:
        app.magnet_btn.configure(
            text="MAGNEET AAN",
            fg_color="green"
        )
    else:
        app.magnet_btn.configure(
            text="MAGNEET UIT",
            fg_color="gray"
        )
