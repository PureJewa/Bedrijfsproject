# CommunicationConfig.py
# Config file for PLC communication settings

# Here you can set the PLC connection parameters and data offsets
PLC_IP = "192.168.10.1"
RACK = 0
SLOT = 1
DB_NUM = 1
# Max motor speed in degrees per second
MAX_SPEED_DEG_PER_S = 18000.0
# Max motor acceleration in degrees per second squared
MAX_ACCEL_DEG_PER_S2 = 90000.0
# Max amount of pallets
MAX_PALLETS = 3
# Max amount of cycles (sheets)
MAX_CYCLES = 5
# Max joystick speed
MAX_JOYSTICK_SPEED = 5000.0
# Max coordinate value
MAX_COORD_X = 1000.0
MAX_COORD_Y = 1000.0
MAX_COORD_Z = 500.0
# Here you can set BITS for the offsets of the data blocks
# Format: "Bit_Name": (Byte_Index, Bit_Index)
BITS_ALL = {
    "Power_Python":             (0, 0),
    "Start_Python":             (0, 1),
    "Stop_Python":              (0, 2),
    "Pauze_Python":             (0, 3),
    "Reset_Python":             (0, 4),
    "Home_Python":              (0, 5),
    "Move_Python":              (0, 6),
    "Go_QR_Python":             (0, 7),
    "Magneet_Python":           (2, 0),
    "Move_Pick_Python":         (2, 1),
    "Move_Place_Python":        (2, 2),
    "Send_Coords":              (2, 3),
    "QR_Ready_PLC":             (120, 3),
    "Ready_For_Coord_PLC":      (120, 4),
    "At_Pick_Coordinate_PLC":   (120, 5),
    "At_Place_Coordinate_PLC":  (120, 6),



    "Forward_X_Python":    (1, 0),
    "Backward_X_Python":   (1, 1),
    "Forward_Y_Python":    (1, 2),
    "Backward_Y_Python":   (1, 3),
    "Forward_Z_Python":    (1, 4),
    "Backward_Z_Python":   (1, 5),
    "Forward_R_Python":    (1, 6), #Right rotation
    "Backward_R_Python":   (1, 7), #Left rotation
}

# For easier access, we separate control and motion bits
CONTROL_BITS = [
    "Start_Python", "Stop_Python", "Pauze_Python", "Reset_Python",
    "Home_Python", "Move_Python", "GoHome_Python",
]
MOTION_BITS = [
    "Forward_X_Python", "Backward_X_Python",
    "Forward_Y_Python", "Backward_Y_Python",
    "Forward_Z_Python", "Backward_Z_Python",
    "Forward_R_Python", "Backward_R_Python",
]

# Here you can set REAL offsets for the data blocks
# Format: "Real_Name": Byte_Index
LREAL_OFFSETS = {
    "X_Speed_Python": 4,
    "Y_Speed_Python": 12,
    "Z_Speed_Python": 20,
    "R_speed_Python": 28,

    "Joystick_X_speed": 36,
    "Joystick_Y_speed": 44,
    "Joystick_Z_speed": 52,
    "Joystick_R_speed": 60,

    "Pick_X_Coord_Python": 72,
    "Pick_Y_Coord_Python": 80,
    "Pick_Z_Coord_Python": 88,

    "Place_X_Coord_Python": 96,
    "Place_Y_Coord_Python": 104,
    "Place_Z_Coord_Python": 112,
}

# Here you can set INT offsets for the data blocks
# Format: "Int_Name": Byte_Index
INT_OFFSETS = {
    "Pallet_Amount": 68,
    "Sheet_Amount": 70,
}