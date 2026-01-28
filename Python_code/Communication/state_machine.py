# state_machine.py
from Python_code.Communication.communicationTia import *
from Python_code.Communication.communicationConfig import *
import time
import datetime
import json
from enum import Enum
placeX = 0.0
placeY = 0.0

class PLCState(Enum):
    IDLE = 0
    GO_QR = 1
    WAIT_QR = 2
    SEND_PICK = 3
    MOVE_PICK = 4
    SEND_PLACE = 5
    MOVE_PLACE = 6
    DONE = 7
    AT_PLACE = 8


class PLCSequence:
    def __init__(self, vision, gui):
        self.state = PLCState.IDLE
        self.coords = None
        self.vision = vision
        self.gui = gui
        self.gui.resetStatemachine = False
        self.prev_state = None
        self.pick_sent = False
        self.place_sent = False
        self.z = -226  # Hoogte voor pick actie

    def step(self):
        if self.gui.resetStatemachine:
            write_log("PLC state machine reset")
            self.state = PLCState.IDLE
            self.coords = None
            self.gui.resetStatemachine = False
            self.pick_sent = False
            self.place_sent = False
            set_bit("Start_Python", False)
            set_bit("Move_Python", False)
            set_bit("Home_Python", False)
            set_bit("Go_QR_Python", False)
            set_bit("Send_Coords", False)
            set_bit("Move_Pick_Python", False)
            set_bit("Move_Place_Python", False)

        if self.state != self.prev_state:
            write_log(f"PLC state changed to {self.state.name}")
            self.prev_state = self.state
        if self.state == PLCState.IDLE:
            if get_bit("Start_Python"):
                set_bit("Move_Python", False)
                set_bit("Home_Python", False)
                set_bit("Go_QR_Python", True)
                self.vision.start()
                self.state = PLCState.WAIT_QR

        elif self.state == PLCState.WAIT_QR:
            set_bit("Go_QR_Python", False)
            if get_bit("QR_Ready_PLC"):
                coords = self.vision.get_coordinates()
                if coords is not None:
                    self.coords = coords
                    self.state = PLCState.SEND_PICK

        elif self.state == PLCState.SEND_PICK:
            # Alleen sturen als nog niet gestuurd
            set_bit("Send_Coords", True)
            if get_bit("Ready_For_Coord_PLC"):
                point = self.coords[0]
                if not self.pick_sent:
                    write_pick_coord(point["x"], point["y"], self.z)
                    write_log("Pick coordinate sent")
                    self.pick_sent = True

                # Controleer of PLC de coordinaat accepteert
                if check_pick_coord(point["x"], point["y"], self.z):
                    write_log("Pick coordinate accepted")
                    self.pick_sent = False
                    self.state = PLCState.MOVE_PICK

        elif self.state == PLCState.MOVE_PICK:
            set_bit("Send_Coords", False)
            set_bit("Move_Pick_Python", True)
            if get_bit("At_Pick_Coordinate_PLC"):
                set_bit("Move_Pick_Python", False)
                set_bit("Move_To_SafeSpot_Python", True)
                if get_bit("At_SafeSpot_PLC"):
                    set_bit("Move_To_SafeSpot_Python", False)
                    if not self.place_sent:
                        placeX = 340
                        placeY = 500
                        write_place_coord(placeX, placeY, self.z)
                        write_log("Place coordinate sent")
                        self.place_sent = True
                    if check_place_coord(placeX, placeY, self.z):
                        write_log("Place coordinate accepted")
                        self.place_sent = False
                        self.state = PLCState.AT_PLACE

        elif self.state == PLCState.MOVE_PLACE:
            set_bit("Move_Place_Python", True)
            if get_bit("At_Place_Coordinate_PLC"):
                self.state = PLCState.SEND_PLACE

        elif self.state == PLCState.SEND_PLACE:
            set_bit("Move_Place_Python", False)
            if get_bit("Ready_For_Coord_PLC"):
                set_bit("Move_Python", True)
                set_bit("Move_Python", False)
                self.state = PLCState.DONE

        elif self.state == PLCState.DONE:
            used_point = pop_first_coordinate(self.vision)
            write_log(f"Point consumed: {used_point}")

            # Als er nog punten zijn → opnieuw picken
            if self.vision.get_coordinates():
                self.state = PLCState.SEND_PICK
            else:
                self.state = PLCState.IDLE


def write_pick_coord(X, Y, Z):
    write_lreal("Pick_X_Coord_Python", X)
    write_lreal("Pick_Y_Coord_Python", Y)
    write_lreal("Pick_Z_Coord_Python", Z)


def write_place_coord(X, Y, Z):
    write_lreal("Place_X_Coord_Python", X)
    write_lreal("Place_Y_Coord_Python", Y)
    write_lreal("Place_Z_Coord_Python", Z)


def pop_first_coordinate(vision):
    """
    Verwijdert het eerste punt uit Vision-geheugen én JSON
    """
    with vision.lock:
        if not vision.coords or len(vision.coords) == 0:
            return None

        used_point = vision.coords.pop(0)

        payload = {
            "points": vision.coords
        }

        with open(vision.json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

        return used_point


def check_pick_coord(X, Y, Z):
    pick_x = read_lreal("Pick_X_Coord_Python")
    pick_y = read_lreal("Pick_Y_Coord_Python")
    pick_z = read_lreal("Pick_Z_Coord_Python")
    write_log(f"Checking pick coord: PLC({pick_x}, {pick_y}, {pick_z}) vs Sent({X}, {Y}, {Z})")
    if X == pick_x and Y == pick_y and Z == pick_z:
        return True

def check_place_coord(X,Y,Z):
    place_x = read_lreal("Place_X_Coord_Python")
    place_y = read_lreal("Place_Y_Coord_Python")
    place_z = read_lreal("Place_Z_Coord_Python")
    write_log(f"Checking place coord: PLC({place_x}, {place_y}, {place_z}) vs Sent({X}, {Y}, {Z})")
    if X == place_x and Y == place_y and Z == place_z:
        return True
