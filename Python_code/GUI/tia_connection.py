import snap7
from Python_code.Logger.logger import write_log
from snap7.util import set_bool, get_lreal
import struct
PLC_IP = "192.168.10.1"   # <-- jouw PLC IP
RACK   = 0
SLOT   = 1
PyInDB = 1               # DB1 (niet-geoptimaliseerd!)
PyOutDB = 26
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
    """Read-modify-write één bit in één byte."""
    plc_connect()
    data = bytearray(client.db_read(PyInDB, byte_index, 1))
    set_bool(data, 0, bit_index, bool(value))
    client.db_write(PyInDB, byte_index, data)




startPLC = (0, 0)  # DB, start, size
stopPLC = (0,1)   # DB, start, size
pausePLC = (0, 3)  # DB, start, size
resetPLC = (0, 4)  # DB, start, size
movePLC = (0, 5)   # DB, start, size
homePLC = (0, 6)   # DB, start, size
GoHomePLC = (0, 7) # DB, start, size

Forward_X = (1, 0)  # DB, start, size
Backward_X = (1, 1)  # DB, start, size
Forward_Y = (1, 2)  # DB, start, size
Backward_Y = (1, 3)  # DB, start, size
Forward_Z = (1, 4)  # DB, start, size
Backward_Z = (1, 5)  # DB, start, size
#
X_CoordinatePLC = (2, 200)  # DB, start
Y_CoordinatePLC = (10, 200)  # DB, start
Z_CoordinatePLC = (18, 200)  # DB, start

X_Speed = (26, 200)  # DB, start
Y_Speed = (34, 300)  # DB, start
Z_Speed = (42, 400)  # DB, start

#
# emergencyPLC = (1, 5, 1)  # DB, start, size
#
# speedPLC = (2, 0)
# accelerationPLC = (2, 2)
# cyclesPLC = (2, 4)
# # ----------------------------------------
# # Function to connect to a TIA Portal PLC
# # ----------------------------------------
# def TIAConnection(ip, rack, slot):
#     try:
#         client = snap7.client.Client()
#         client.connect(ip, rack, slot)
#         if client.get_connected():
#             write_log(f"Connected to PLC at {ip} (Rack: {rack}, Slot: {slot})")
#         return client
#     except Exception as e:
#         write_log(f"Connection error: {e}")
#         return None
#
# # ----------------------------------------
# # Functions to communicate with a PLC (Siemens)
# # We can send and receive different types of data: BOOL, INT, FLOAT, STRING
# # ----------------------------------------
#
# # --- Send a single boolean (True/False) to the PLC ---
# def send_bool(client, db_number, byte_index, bit_index, value):
#     try:
#         # Check if we are connected to the PLC
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())  # Try to reconnect
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return
#
#         # Read the current data block from PLC
#         data = bytearray(client.db_read(db_number, byte_index, 1))
#         set_bool(data, 0, bit_index, bool(value))
#         client.db_write(db_number, byte_index, data)
#
#     except Exception as e:
#         write_log(f"Error sending bool data to PLC: {e}")  # Log any errors
#
#
# # --- Receive a single boolean (True/False) from the PLC ---
# def receiveBool(client, db_number, start, size):
#     try:
#         # Check connection
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return None
#
#         # Read the data block from PLC (1 byte for a single BOOL)
#         data = client.db_read(db_number, start, 1)
#
#         # Extract the boolean value
#         bit = get_bool(data, start, size)
#         return bit
#
#     except Exception as e:
#         write_log(f"Error receiving data from PLC: {e}")
#         return None
#
#
# # --- Send a 16-bit integer to the PLC ---
# def sendInt(client, db_number, start, value):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return
#
#         # INT = 2 bytes (16 bits)
#         data = bytearray(2)
#
#         # Convert the integer into bytes and store in data
#         set_int(data, 0, value)
#
#         # Write the data block to the PLC
#         client.db_write(db_number, start, data)
#
#     except Exception as e:
#         write_log(f"Error sending int data to PLC: {e}")
#
#
# # --- Receive a 16-bit integer from the PLC ---
# def receiveInt(client, db_number, start):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return None
#
#         # Read 2 bytes from PLC
#         data = client.db_read(db_number, start, 2)
#         return get_int(data, 0)  # Convert bytes back to integer
#
#     except Exception as e:
#         write_log(f"Error receiving int data from PLC: {e}")
#         return None
#
#
# # --- Send a 32-bit floating point number (REAL) to the PLC ---
# def sendFloat(client, db_number, start, value):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return
#
#         # REAL = 4 bytes
#         data = bytearray(4)
#
#         # Convert the float into bytes and store in data
#         set_real(data, 0, value)
#
#         # Write to PLC
#         client.db_write(db_number, start, data)
#
#     except Exception as e:
#         write_log(f"Error sending float data to PLC: {e}")
#
#
# # --- Receive a 32-bit floating point number from the PLC ---
# def receiveFloat(client, db_number, start):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return None
#
#         # Read 4 bytes from PLC (REAL)
#         data = client.db_read(db_number, start, 4)
#         return get_real(data, 0)  # Convert bytes to float
#
#     except Exception as e:
#         write_log(f"Error receiving float data from PLC: {e}")
#         return None
#
#
# # --- Send a string (text) to the PLC ---
# def sendString(client, db_number, start, value, max_length=20):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return
#
#         # Create a byte array: max_length + 2 bytes for string header
#         data = bytearray(max_length + 2)
#
#         # Convert the string into bytes and store in data
#         set_string(data, 0, value, max_length)
#
#         # Write to PLC
#         client.db_write(db_number, start, data)
#
#     except Exception as e:
#         write_log(f"Error sending string data to PLC: {e}")
#
#
# # --- Receive a string (text) from the PLC ---
# def receiveString(client, db_number, start, max_length=20):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return None
#
#         # Read bytes from PLC (max_length + 2 for string header)
#         data = client.db_read(db_number, start, max_length + 2)
#
#         # Convert bytes to string
#         return get_string(data, 0, max_length)
#
#     except Exception as e:
#         write_log(f"Error receiving string data from PLC: {e}")
#         return None
#
def write_lreal(byte_index: int, value: float):
    """Schrijf LREAL (64-bit) in big-endian (S7-volgorde)."""
    plc_connect()
    b = struct.pack(">d", float(value))
    client.db_write(PyInDB, byte_index, b)
def read_bits_bytes(num_bytes: int = 2) -> bytes:
    """Lees een paar bytes voor de booleans (standaard 2 bytes)."""
    plc_connect()
    return client.db_read(PyOutDB, 0, num_bytes)

def sendLreal(byte_index: int, value: float):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return

        # Convert the float into bytes and store in data
        b = struct.pack(">d", float(value))

        # Write to PLC
        client.db_write(PyInDB, byte_index, b)

    except Exception as e:
        write_log(f"Error sending Lreal data to PLC: {e}")

def recieveLreal(db_number, start):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return None

        # Read 8 bytes from PLC (LREAL)
        data = client.db_read(db_number, start, 8)
        return get_lreal(data, 0)  # Convert bytes to float

    except Exception as e:
        write_log(f"Error receiving Lreal data from PLC: {e}")
        return None
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
