# config_screens.py

# Imports from project
from Python_code.Communication.communicationTia import *
from Python_code.Communication.communicationConfig import *

topButtons = ['Home', 'Settings', 'Log', 'Test', 'Control PLC']
homeScreenButtons = ['Start', 'Pause', 'Stop', 'Homing', 'Reset', 'Camera']
settingsScreenButtons = ['Speed', "Acceleration", "Cycles", "Pallets", "Pick coordinates", "Place coordinates"]
testButtons = ['Forward X', 'Backward X', 'Forward Y', 'Backward Y', 'Forward Z', 'Backward Z', 'X coord', 'Y coord', 'Z coord','Set Speed X', 'Set Speed Y', 'Set Speed Z', 'Emergency Stop']
testButtonsV1 = ['Send Bool', 'Receive Bool', 'Send Int', 'Receive Int', 'Send Float', 'Receive Float', 'Send String', 'Receive String', 'Send Lreal', 'Receive Lreal']
lampColors = ['Green', 'Yellow', 'Red']

motors = ["X-motor", "Y-motor", "Z-motor"]
devices = ["PLC", *motors, "Gripper", "Daheng camera", "Logitech camera", 'X-endstop', 'Y-endstop', 'Z-endstop']

setting_widgets = {
    "Speed": {
        "entries": [
            ("speedEntryX", "Set speed for X axis"),
            ("speedEntryY", "Set speed for Y axis"),
            ("speedEntryZ", "Set speed for Z axis"),
        ],
        "button_text": "Set Speed",
        "use_grid": True
    },

    "Acceleration": {
        "entries": [
            ("accelEntryX", "Set Acceleration X axis"),
            ("accelEntryY", "Set Acceleration Y axis"),
            ("accelEntryZ", "Set Acceleration Z axis"),
        ],
        "button_text": "Set Acceleration",
        "use_grid": True
    },

    "Cycles": {
        "entries": [
            ("cyclesEntry", "Set Number of Cycles"),
        ],
        "button_text": "Set Cycles",
        "use_grid": False
    },

    "Pallets": {
        "entries": [
            ("palletsEntry", "Set Number of Pallets"),
        ],
        "button_text": "Set Pallets",
        "use_grid": False
    },

    "Pick coordinates": {
        "entries": [
            ("pickXEntry", "Set Pick X Coordinate"),
            ("pickYEntry", "Set Pick Y Coordinate"),
            ("pickZEntry", "Set Pick Z Coordinate"),
        ],
        "button_text": "Set Pick Coordinates",
        "use_grid": True
    },

    "Place coordinates": {
        "entries": [
            ("placeXEntry", "Set Place X Coordinate"),
            ("placeYEntry", "Set Place Y Coordinate"),
            ("placeZEntry", "Set Place Z Coordinate"),
        ],
        "button_text": "Set Place Coordinates",
        "use_grid": True
    },
}
#Home button actions
ACTIONS = {
    "Start": {
        "log": "Starting process",
        "bit": "Start_Python",
        "reset": ["Pauze_Python", "Stop_Python", "Reset_Python"]
    },
    "Pause": {
        "log": "Pausing process",
        "bit": "Pauze_Python",
        "reset": ["Start_Python", "Stop_Python", "Reset_Python"]
    },
    "Stop": {
        "log": "Stopping process",
        "bit": "Stop_Python",
        "reset": ["Start_Python", "Pauze_Python", "Reset_Python"]
    },
    "Homing": {
        "log": "Going Home!",
        "bit": "Home_Python",
        "reset": ["Pauze_Python", "Stop_Python", "Reset_Python"]
    },
    "Reset": {
        "log": "Resetting process",
        "bit": "Reset_Python",
        "reset": ["Start_Python", "Pauze_Python", "Stop_Python"]
    }
}
