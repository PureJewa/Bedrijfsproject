# control_screen.py

# Imports from python libs
import customtkinter as ctk
import math
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading

# Imports within the project
from Python_code.Logger.logger import *
from Python_code.Communication.communicationTia import *
from Python_code.Communication.communicationConfig import *

def camera_thread(app):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    app.cap = cap

    while app.camera_running:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        app.latest_frame = frame

    cap.release()

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
    mainFrame.rowconfigure(0, weight=1)

    # =========================
    # Left / Center / Right
    # =========================
    leftFrame = ctk.CTkFrame(mainFrame, corner_radius=12)
    centerFrame = ctk.CTkFrame(mainFrame, corner_radius=12)
    rightFrame = ctk.CTkFrame(mainFrame, corner_radius=12)

    leftFrame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
    centerFrame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
    rightFrame.grid(row=0, column=2, sticky="nsew", padx=8, pady=8)

    # =========================
    # Joystick percentage display (top, spans all)
    # =========================
    infoFrame = ctk.CTkFrame(mainFrame)
    infoFrame.grid(row=1, column=0, columnspan=3, pady=(4, 8))

    ctk.CTkLabel(infoFrame, text="X:").grid(row=0, column=0, padx=5)
    ctk.CTkLabel(infoFrame, textvariable=app.pct_x).grid(row=0, column=1, padx=5)
    ctk.CTkLabel(infoFrame, text="Y:").grid(row=0, column=2, padx=5)
    ctk.CTkLabel(infoFrame, textvariable=app.pct_y).grid(row=0, column=3, padx=5)
    ctk.CTkLabel(infoFrame, text="Z:").grid(row=0, column=4, padx=5)
    ctk.CTkLabel(infoFrame, textvariable=app.pct_z).grid(row=0, column=5, padx=5)

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
    app.camera_image = None
    app.latest_frame = None
    app.camera_running = True

    t = threading.Thread(target=camera_thread, args=(app,), daemon=True)
    t.start()

    def update_canvas():
        if app.latest_frame is not None:
            frame = app.latest_frame

            cw = app.cameraCanvas.winfo_width()
            ch = app.cameraCanvas.winfo_height()

            if cw > 1 and ch > 1:
                frame = cv2.resize(frame, (cw, ch))

            img = Image.fromarray(frame)
            app.camera_image = ImageTk.PhotoImage(img)

            app.cameraCanvas.delete("all")
            app.cameraCanvas.create_image(0, 0, anchor="nw", image=app.camera_image)

        app.cameraCanvas.after(1, update_canvas)

    update_canvas()

    # Placeholder crosshair
    w, h = 480, 360
    app.cameraCanvas.create_line(w//2, 0, w//2, h, fill="gray")
    app.cameraCanvas.create_line(0, h//2, w, h//2, fill="gray")


# ==========================================================
# Logic (UNCHANGED)
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
            write_lreal(LREAL_OFFSETS[name], value)
            app.last_speed[name] = value
        except Exception as e:
            write_log(f"Error writing speed {name}: {e}")


def apply_bits(app, desired: dict):
    for name, state in desired.items():
        try:
            set_bit(name, state)
        except Exception as e:
            write_log(f"Error writing bit {name}: {e}")


def handle_axis(app, axis: str, val: float, fwd_bit: str, bwd_bit: str, speed_name: str):
    th = float(app.threshold.get())

    if val > th:
        direction = 1
    elif val < -th:
        direction = -1
    else:
        direction = 0

    speed = 0.0 if direction == 0 else scaled_percent(app, val)
    write_speed_if_changed(app, speed_name, speed)

    if direction == 1:
        apply_bits(app, {fwd_bit: True, bwd_bit: False})
    elif direction == -1:
        apply_bits(app, {fwd_bit: False, bwd_bit: True})
    else:
        apply_bits(app, {fwd_bit: False, bwd_bit: False})

    pct = abs(speed)
    if axis == "X":
        app.pct_x.set(f"{pct:.0f}%")
    elif axis == "Y":
        app.pct_y.set(f"{pct:.0f}%")
    elif axis == "Z":
        app.pct_z.set(f"{pct:.0f}%")


def on_xy(app, x, y):
    handle_axis(app, "X", x, "Forward_X_Python", "Backward_X_Python", "Joystick_X_speed")
    handle_axis(app, "Y", y, "Forward_Y_Python", "Backward_Y_Python", "Joystick_Y_speed")


def on_z(app, _x, y):
    handle_axis(app, "Z", y, "Forward_Z_Python", "Backward_Z_Python", "Joystick_Z_speed")


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
