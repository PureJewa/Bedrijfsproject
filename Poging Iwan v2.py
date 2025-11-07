# CTk PLC Controller – Realtime joystick (0–100% scaling), Toggles, LREALs, Settings
# Vereisten: pip install customtkinter python-snap7

import math
import struct
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

import snap7
from snap7.util import set_bool

# =======================
# PLC CONFIG
# =======================
PLC_IP = "192.168.10.1"   # <-- jouw PLC IP
RACK   = 0
SLOT   = 1
DB_NUM = 1                # DB1 (niet-geoptimaliseerd!)

# Max motorsnelheid (graden/seconde)
MAX_SPEED_DEG_PER_S = 18000.0   # nieuw maximum

# =======================
# BIT MAPPING (volgens jouw DB)
# Byte 0:
# 0.0 Start_Python, 0.1 Stop_Python, 0.2 Pauze_Python, 0.3 Reset_Python,
# 0.4 Home_Python, 0.5 Move_Python, 0.6 GoHome_Python
# Byte 1:
# 1.0 Forward_X_Python, 1.1 Backward_X_Python,
# 1.2 Forward_Y_Python, 1.3 Backward_Y_Python,
# 1.4 Forward_Z_Python, 1.5 Backward_Z_Python
# =======================
BITS_ALL = {
    "Start_Python":        (0, 0),
    "Stop_Python":         (0, 1),
    "Pauze_Python":        (0, 2),
    "Reset_Python":        (0, 3),
    "Home_Python":         (0, 4),
    "Move_Python":         (0, 5),
    "GoHome_Python":       (0, 6),

    "Forward_X_Python":    (1, 0),
    "Backward_X_Python":   (1, 1),
    "Forward_Y_Python":    (1, 2),
    "Backward_Y_Python":   (1, 3),
    "Forward_Z_Python":    (1, 4),
    "Backward_Z_Python":   (1, 5),
}

CONTROL_BITS = [
    "Start_Python", "Stop_Python", "Pauze_Python", "Reset_Python",
    "Home_Python", "Move_Python", "GoHome_Python",
]
MOTION_BITS = [
    "Forward_X_Python", "Backward_X_Python",
    "Forward_Y_Python", "Backward_Y_Python",
    "Forward_Z_Python", "Backward_Z_Python",
]

# =======================
# LREAL OFFSETS
# =======================
LREAL_OFFSETS = {
    # (optionele) posities
    "X_Coord_Python":  2,
    "Y_Coord_Python": 10,
    "Z_Coord_Python": 18,

    # Gecommandeerde snelheden (handmatig invullen)
    "X_Speed_Python": 26,   # offset 26.0
    "Y_Speed_Python": 34,   # offset 34.0
    "Z_Speed_Python": 42,   # offset 42.0

    # Joystick snelheden (worden continu geschreven door de joystick)
    "Joystick_X_speed": 50, # offset 50.0
    "Joystick_Y_speed": 58, # offset 58.0
    "Joystick_Z_speed": 66, # offset 66.0
}

# =======================
# SNAP7 HELPERS
# =======================
client = snap7.client.Client()

def plc_connect():
    if not client.get_connected():
        client.connect(PLC_IP, RACK, SLOT)

def plc_disconnect():
    try:
        if client.get_connected():
            client.disconnect()
    except Exception:
        pass

def write_bool(byte_index: int, bit_index: int, value: bool):
    plc_connect()
    data = bytearray(client.db_read(DB_NUM, byte_index, 1))
    set_bool(data, 0, bit_index, bool(value))
    client.db_write(DB_NUM, byte_index, data)

def read_bytes(start: int, length: int) -> bytes:
    plc_connect()
    return client.db_read(DB_NUM, start, length)

def write_lreal(byte_index: int, value: float):
    plc_connect()
    b = struct.pack(">d", float(value))  # S7 big-endian
    client.db_write(DB_NUM, byte_index, b)

def read_lreal(byte_index: int) -> float:
    plc_connect()
    b = client.db_read(DB_NUM, byte_index, 8)
    return struct.unpack(">d", b)[0]

# =======================
# UI WIDGETS
# =======================
class Indicator(ctk.CTkFrame):
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

class ToggleButton(ctk.CTkButton):
    def __init__(self, master, text_on="ON", text_off="OFF", initial=False, command_toggle=None, **kwargs):
        super().__init__(master, **kwargs)
        self.state_on = bool(initial)
        self.text_on = text_on
        self.text_off = text_off
        self.command_toggle = command_toggle
        self.configure(command=self._on_press, width=78, height=30)
        self._refresh()

    def _on_press(self):
        self.state_on = not self.state_on
        if self.command_toggle:
            self.command_toggle(self.state_on)
        self._refresh()

    def set_state(self, on: bool):
        self.state_on = bool(on)
        self._refresh()

    def _refresh(self):
        if self.state_on:
            self.configure(text=self.text_on, fg_color="#1f6aa5")
        else:
            self.configure(text=self.text_off, fg_color="#3a3a3a")

class Joystick(ctk.CTkFrame):
    """Virtuele joystick; geeft genormaliseerde x,y [-1..1] via on_change; veert naar 0 bij loslaten."""
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

        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)

    def _center(self):
        self._set_knob(self.r, self.r)
        if self.on_change:
            self.on_change(0.0, 0.0)

    def _set_knob(self, cx, cy):
        r = self.knob_r
        self.canvas.coords(self.knob, cx - r, cy - r, cx + r, cy + r)

    def _process(self, x, y):
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
        self._set_knob(cx, cy)
        nx = vx / max_radius
        ny = -vy / max_radius  # omhoog = +
        if self.on_change:
            self.on_change(nx, ny)

    def _click(self, e):   self._process(e.x, e.y)
    def _drag(self, e):    self._process(e.x, e.y)
    def _release(self, _): self._center()

# =======================
# APP MET TABBLADEN
# =======================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PLC Controller – Tabs")
        self.geometry("1100x740")
        self.minsize(900, 560)
        self.resizable(True, True)

        # parameters
        self.deadzone  = tk.DoubleVar(value=0.20)  # dode zone voor % én speed
        self.threshold = tk.DoubleVar(value=0.30)  # richting-bits (mag iets lager dan deadzone voor soepel wisselen)
        self.ui_scale  = tk.DoubleVar(value=1.0)

        # caches
        self.last_state = {name: None for name in BITS_ALL.keys()}
        self.last_speed = {
            "Joystick_X_speed": None,
            "Joystick_Y_speed": None,
            "Joystick_Z_speed": None,
        }
        # laatste richting die op de RICHTING-bits is gezet (-1/0/1)
        self.axis_last_bits_sign = {"X": 0, "Y": 0, "Z": 0}

        # live % labels
        self.pct_x = tk.StringVar(value="0%")
        self.pct_y = tk.StringVar(value="0%")
        self.pct_z = tk.StringVar(value="0%")

        self._build_ui()
        self._poll()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- UI ----------
    def _build_ui(self):
        # header
        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(top, text="DB1 Controller (Joystick • Toggles • LREALs • Settings)",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=12, pady=8)
        self.status_lbl = ctk.CTkLabel(top, text="Status: niet verbonden", text_color="gray70")
        self.status_lbl.pack(side="right", padx=12)

        # tabs
        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=12, pady=(0,12))

        self.tab_joy     = tabs.add("Joystick")
        self.tab_toggles = tabs.add("Toggles")
        self.tab_lreals  = tabs.add("LREALs")
        self.tab_settings= tabs.add("Settings")

        # === Joystick tab ===
        joy_left = ctk.CTkFrame(self.tab_joy, corner_radius=12)
        joy_right= ctk.CTkFrame(self.tab_joy, corner_radius=12)
        joy_left.pack(side="left",  fill="both", expand=True, padx=(0,8), pady=8)
        joy_right.pack(side="right", fill="y", padx=(8,0), pady=8)

        self.jxy = Joystick(joy_left, label="Joystick X/Y (−100…+100%)  →  ±18 000 °/s",
                            diameter=240, on_change=self._on_xy)
        self.jxy.pack(side="left", padx=12, pady=12)

        self.jz  = Joystick(joy_left, label="Joystick Z (−100…+100%)   →  ±18 000 °/s",
                            diameter=240, only_vertical=True, on_change=self._on_z)
        self.jz.pack(side="left", padx=12, pady=12)

        # live % panel
        card = ctk.CTkFrame(joy_right, corner_radius=12)
        card.pack(fill="x", padx=12, pady=(12,8))
        ctk.CTkLabel(card, text="Live Joystick %", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=12, pady=(10,6))
        row = ctk.CTkFrame(card, fg_color="transparent"); row.pack(fill="x", padx=12, pady=(0,10))
        ctk.CTkLabel(row, text="X:").pack(side="left"); ctk.CTkLabel(row, textvariable=self.pct_x).pack(side="left", padx=(4,16))
        ctk.CTkLabel(row, text="Y:").pack(side="left"); ctk.CTkLabel(row, textvariable=self.pct_y).pack(side="left", padx=(4,16))
        ctk.CTkLabel(row, text="Z:").pack(side="left"); ctk.CTkLabel(row, textvariable=self.pct_z).pack(side="left", padx=(4,16))

        # noodstop en debug
        ctk.CTkButton(joy_right, text="Noodstop (alle beweging uit)", fg_color="#ff3b30", hover_color="#c02a22",
                      command=self._motion_off).pack(fill="x", padx=12, pady=(10,8))
        self.debug_box = ctk.CTkTextbox(joy_right, width=320, height=440)
        self.debug_box.pack(fill="both", expand=True, padx=12, pady=8)
        self._dbg({"Info": "Joystick actief"})

        # === Toggles tab ===
        ctk.CTkLabel(self.tab_toggles, text="Besturingsbits",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=12, pady=(12,8))
        tbox = ctk.CTkFrame(self.tab_toggles, corner_radius=12)
        tbox.pack(fill="x", padx=12, pady=(0,12))

        self.toggle_buttons = {}
        for name in CONTROL_BITS:
            row = ctk.CTkFrame(tbox, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(row, text=name).pack(side="left")
            btn = ToggleButton(row, text_on="ON", text_off="OFF",
                               command_toggle=lambda state, n=name: self._set_bit(n, state))
            btn.pack(side="right")
            self.toggle_buttons[name] = btn

        # indicatoren
        ind = ctk.CTkFrame(self.tab_toggles, corner_radius=12)
        ind.pack(fill="x", padx=12, pady=(0,12))
        ctk.CTkLabel(ind, text="Indicatie lampjes", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=12, pady=(10,4))
        row = ctk.CTkFrame(ind, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(6,10))
        self.ind_start = Indicator(row, "Start",  "#31d843"); self.ind_start.pack(side="left", padx=(0,16))
        self.ind_stop  = Indicator(row, "Stop",   "#ff3b30"); self.ind_stop.pack(side="left", padx=(0,16))
        self.ind_reset = Indicator(row, "Reset",  "#ff9500"); self.ind_reset.pack(side="left", padx=(0,16))
        self.ind_pause = Indicator(row, "Pauze",  "#ffd60a"); self.ind_pause.pack(side="left", padx=(0,16))

        # === LREALs tab ===
        lbox = ctk.CTkFrame(self.tab_lreals, corner_radius=12)
        lbox.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(lbox, text="LREAL waardes (coördinaten & joystick/command-snelheden in °/s)",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=12)
        self.lreal_entries = {}
        def add_ent(lbl, r, default="0.0"):
            ctk.CTkLabel(lbox, text=f"{lbl} (offset {LREAL_OFFSETS[lbl]}.0)").grid(row=r, column=0, sticky="w", padx=12, pady=6)
            e = ctk.CTkEntry(lbox, width=260); e.insert(0, default); e.grid(row=r, column=1, sticky="w", pady=6)
            self.lreal_entries[lbl] = e

        r=1
        # coords
        add_ent("X_Coord_Python", r); r+=1
        add_ent("Y_Coord_Python", r); r+=1
        add_ent("Z_Coord_Python", r); r+=1

        ctk.CTkLabel(lbox, text="—"*46).grid(row=r, column=0, columnspan=2, sticky="ew", padx=12, pady=(6,6)); r+=1

        # commanded speeds (26/34/42)
        add_ent("X_Speed_Python", r, "0.0"); r+=1
        add_ent("Y_Speed_Python", r, "0.0"); r+=1
        add_ent("Z_Speed_Python", r, "0.0"); r+=1

        ctk.CTkLabel(lbox, text="—"*46).grid(row=r, column=0, columnspan=2, sticky="ew", padx=12, pady=(6,6)); r+=1

        # joystick speeds (50/58/66)
        add_ent("Joystick_X_speed", r, "0.0"); r+=1
        add_ent("Joystick_Y_speed", r, "0.0"); r+=1
        add_ent("Joystick_Z_speed", r, "0.0"); r+=1

        btns = ctk.CTkFrame(lbox, fg_color="transparent"); btns.grid(row=r, column=0, columnspan=2, sticky="w", padx=12, pady=(8,12))
        ctk.CTkButton(btns, text="Schrijf alle LREALs → PLC", command=self._write_all_lreals).pack(side="left", padx=(0,10))
        ctk.CTkButton(btns, text="Lees alle LREALs ← PLC",   command=self._read_all_lreals).pack(side="left")

        # === Settings tab ===
        sbox = ctk.CTkFrame(self.tab_settings, corner_radius=12)
        sbox.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(sbox, text="Joystick SETTINGS", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12,8))
        ctk.CTkLabel(sbox, text="Deadzone (voor % en speed)").grid(row=1, column=0, sticky="w", padx=12, pady=6)
        ctk.CTkSlider(sbox, from_=0.0, to=0.5, number_of_steps=50, variable=self.deadzone).grid(row=1, column=1, sticky="ew", padx=12, pady=6)
        ctk.CTkLabel(sbox, text="Threshold (richting-bits)").grid(row=2, column=0, sticky="w", padx=12, pady=6)
        ctk.CTkSlider(sbox, from_=0.1, to=0.6, number_of_steps=50, variable=self.threshold).grid(row=2, column=1, sticky="ew", padx=12, pady=6)
        ctk.CTkLabel(sbox, text="UI Scale").grid(row=3, column=0, sticky="w", padx=12, pady=(6,12))
        ctk.CTkSlider(sbox, from_=0.8, to=1.3, number_of_steps=50, variable=self.ui_scale, command=self._on_scale).grid(row=3, column=1, sticky="ew", padx=12, pady=(6,12))
        sbox.grid_columnconfigure(1, weight=1)

        conn = ctk.CTkFrame(self.tab_settings, corner_radius=12)
        conn.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(conn, text="Verbinden", command=self._try_connect).pack(side="left", padx=(12,8), pady=10)
        ctk.CTkButton(conn, text="Verbreek",  command=self._disconnect).pack(side="left", padx=8, pady=10)

    # ---------- Scaling helper ----------
    def _scaled_percent(self, axis_val: float) -> float:
        """
        Mooie 0..100% schaal met deadzone:
        |val| <= dz  -> 0%
        anders       -> lineair van 0% tot 100%, geherijkt buiten de deadzone
        """
        dz = float(self.deadzone.get())
        a = abs(axis_val)
        if a <= dz:
            return 0.0
        pct = (a - dz) / max(1e-6, (1.0 - dz))
        pct = max(0.0, min(1.0, pct))
        return pct * 100.0

    # ---------- Speed & bits helpers ----------
    def _speed_signed(self, axis_val: float) -> float:
        """
        Signed snelheid uit 0..100% schaal:
        speed = sign(val) * percent/100 * MAX
        afgerond op 1 decimaal.
        """
        percent = self._scaled_percent(axis_val)  # 0..100
        mag = (percent / 100.0) * MAX_SPEED_DEG_PER_S
        spd = math.copysign(mag, axis_val)
        return max(-MAX_SPEED_DEG_PER_S, min(MAX_SPEED_DEG_PER_S, round(spd, 1)))

    def _write_speed_if_changed(self, name: str, value: float):
        last = self.last_speed.get(name)
        if last is None or abs(value - last) >= 0.1:
            try:
                write_lreal(LREAL_OFFSETS[name], value)
                self.last_speed[name] = value
                ent = self.lreal_entries.get(name)
                if ent is not None:
                    ent.delete(0, "end"); ent.insert(0, f"{value:.1f}")
            except Exception as e:
                messagebox.showerror("Fout bij snelheid schrijven", f"{name}: {e}")

    def _apply_bits(self, desired: dict):
        for name, state in desired.items():
            if self.last_state.get(name) != state:
                b, i = BITS_ALL[name]
                try:
                    write_bool(b, i, state)
                    self.last_state[name] = state
                except Exception as e:
                    messagebox.showerror("Fout bij schrijven bit", f"{name}: {e}")

    # ---------- Realtime axis handler (directe wissel) ----------
    def _handle_axis(self, axis: str, val: float, fwd_bit: str, bwd_bit: str, speed_name: str):
        """
        Realtime besturing:
        - 0..100% schaal (deadzone gecorrigeerd) → ±MAX °/s
        - Richtingbits schakelen direct bij threshold.
        - In het midden (tussen +/- threshold) bits uit en speed 0.
        """
        th = float(self.threshold.get())

        # 1) Speed
        spd = self._speed_signed(val)
        self._write_speed_if_changed(speed_name, spd)

        # 2) Richtingbits
        sign_bits = 1 if val > th else (-1 if val < -th else 0)
        last_bits = self.axis_last_bits_sign[axis]
        if sign_bits != last_bits:
            if sign_bits == 1:
                self._apply_bits({fwd_bit: True,  bwd_bit: False})
            elif sign_bits == -1:
                self._apply_bits({fwd_bit: False, bwd_bit: True})
            else:
                self._apply_bits({fwd_bit: False, bwd_bit: False})
                self._write_speed_if_changed(speed_name, 0.0)
            self.axis_last_bits_sign[axis] = sign_bits

        # 3) Live % label updaten
        percent = abs(self._scaled_percent(val))
        if axis == "X":
            self.pct_x.set(f"{percent:.0f}%")
        elif axis == "Y":
            self.pct_y.set(f"{percent:.0f}%")
        elif axis == "Z":
            self.pct_z.set(f"{percent:.0f}%")

    # ---------- Joystick callbacks ----------
    def _on_xy(self, x, y):
        self._handle_axis("X", x, "Forward_X_Python", "Backward_X_Python", "Joystick_X_speed")
        self._handle_axis("Y", y, "Forward_Y_Python", "Backward_Y_Python", "Joystick_Y_speed")
        self._dbg({"XY": f"x={x:.2f}, y={y:.2f}",
                   "X%": self.pct_x.get(), "Y%": self.pct_y.get()})

    def _on_z(self, _x, y):
        self._handle_axis("Z", y, "Forward_Z_Python", "Backward_Z_Python", "Joystick_Z_speed")
        self._dbg({"Z": f"y={y:.2f}", "Z%": self.pct_z.get()})

    # ---------- Noodstop ----------
    def _motion_off(self):
        self._apply_bits({name: False for name in MOTION_BITS})
        for k in ("Joystick_X_speed", "Joystick_Y_speed", "Joystick_Z_speed"):
            self._write_speed_if_changed(k, 0.0)
        self.axis_last_bits_sign = {"X": 0, "Y": 0, "Z": 0}
        self.pct_x.set("0%"); self.pct_y.set("0%"); self.pct_z.set("0%")

    # ---------- LREALs ----------
    def _write_all_lreals(self):
        try:
            for name, offset in LREAL_OFFSETS.items():
                s = self.lreal_entries[name].get().strip().replace(",", ".")
                val = float(s) if s else 0.0
                write_lreal(offset, val)
        except Exception as e:
            messagebox.showerror("Fout bij LREAL schrijven", str(e))

    def _read_all_lreals(self):
        try:
            for name, offset in LREAL_OFFSETS.items():
                val = read_lreal(offset)
                self.lreal_entries[name].delete(0, "end")
                self.lreal_entries[name].insert(0, f"{val:.6f}")
        except Exception as e:
            messagebox.showerror("Fout bij LREAL lezen", str(e))

    # ---------- Connect & Poll ----------
    def _try_connect(self):
        try:
            plc_connect()
            self._set_status("Verbonden", True)
        except Exception as e:
            self._set_status("Niet verbonden", False)
            messagebox.showerror("Verbinding mislukt", str(e))

    def _disconnect(self):
        try:
            plc_disconnect()
            self._set_status("Verbinding verbroken", False)
        except Exception as e:
            messagebox.showerror("Fout bij verbreken", str(e))

    def _poll(self):
        try:
            if client.get_connected():
                self._set_status("Verbonden", True)
                raw = read_bytes(0, 2)  # 2 bytes met alle booleans
                b0, b1 = raw[0], raw[1]
                bitval = {}
                for name, (b, i) in BITS_ALL.items():
                    byte = b0 if b == 0 else b1
                    bitval[name] = bool((byte >> i) & 0x01)
                    self.last_state[name] = bitval[name]

                # sync toggles en lampjes
                for name in CONTROL_BITS:
                    self.toggle_buttons[name].set_state(bitval[name])

                self.ind_start.set(bitval.get("Start_Python", False))
                self.ind_stop.set(bitval.get("Stop_Python", False))
                self.ind_reset.set(bitval.get("Reset_Python", False))
                self.ind_pause.set(bitval.get("Pauze_Python", False))
            else:
                self._set_status("Niet verbonden", False)
        except Exception:
            self._set_status("Niet verbonden", False)

        self.after(300, self._poll)

    def _set_bit(self, name: str, state: bool):
        b, i = BITS_ALL[name]
        try:
            write_bool(b, i, state)
            self.last_state[name] = state
        except Exception as e:
            messagebox.showerror("Fout bij schrijven bit", f"{name}: {e}")

    def _set_status(self, text, ok: bool):
        self.status_lbl.configure(text=f"Status: {text}", text_color=("#5efc82" if ok else "gray70"))

    def _dbg(self, d: dict):
        if not hasattr(self, "debug_box"):
            return
        self.debug_box.configure(state="normal")
        self.debug_box.delete("1.0", "end")
        for k, v in d.items():
            self.debug_box.insert("end", f"{k}: {v}\n")
        self.debug_box.configure(state="disabled")

    # ---------- UI scale ----------
    def _on_scale(self, _val=None):
        """Live schaal de UI met de slider."""
        try:
            ctk.set_widget_scaling(float(self.ui_scale.get()))
        except Exception:
            pass

    def _on_close(self):
        self._motion_off()
        plc_disconnect()
        self.destroy()

# =======================
# RUN
# =======================
if __name__ == "__main__":
    app = App()
    app.mainloop()
