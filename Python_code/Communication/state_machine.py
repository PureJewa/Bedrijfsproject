# state_machine.py
from Python_code.Communication.communicationTia import *
from Python_code.Communication.communicationConfig import *
import time
from enum import Enum


class PLCState(Enum):
    IDLE = 0
    GO_QR = 1
    WAIT_QR = 2
    SEND_PICK = 3
    MOVE_PICK = 4
    SEND_PLACE = 5
    MOVE_PLACE = 6
    DONE = 7


class PLCSequence:
    def __init__(self):
        self.state = PLCState.IDLE
        self.coords = None

    def step(self):
        if self.state == PLCState.IDLE:
            if get_bit("Start_Python"):
                print("PLC Sequence started")
                set_bit("Move_Python", False)
                set_bit("Home_Python", False)
                set_bit("Go_QR_Python", True)
                self.state = PLCState.GO_QR

        elif self.state == PLCState.GO_QR:
            set_bit("Go_QR_Python", False)
            self.state = PLCState.WAIT_QR

        elif self.state == PLCState.WAIT_QR:
            if get_bit("QR_Ready_PLC"):
                # voorbeeld: QR levert coords via PLC of vision
                pick = {"x": 100.0, "y": 50.0, "z": 30.0}
                place = {"x": 200.0, "y": 80.0, "z": 25.0}
                save_coordinates(pick, place)
                self.coords = load_coordinates()
                self.state = PLCState.SEND_PICK

        elif self.state == PLCState.SEND_PICK:
            if get_bit("Ready_For_Coord_PLC"):
                write_pick_coord(self.coords["pick"])
                if verify_pick_coord(self.coords["pick"]):
                    # set_bit("Move_Python", True)
                    # set_bit("Move_Python", False)
                    self.state = PLCState.MOVE_PICK

        elif self.state == PLCState.MOVE_PICK:
            if get_bit("At_Pick_Coordinate_PLC"):
                self.state = PLCState.MOVE_PLACE

        elif self.state == PLCState.MOVE_PLACE:
            if get_bit("At_Place_Coordinate_PLC"):
                self.state = PLCState.SEND_PLACE

        elif self.state == PLCState.SEND_PLACE:
            if get_bit("Ready_For_Coord_PLC"):
                write_place_coord(self.coords["place"])
                if verify_place_coord(self.coords["place"]):
                    set_bit("Move_Python", True)
                    set_bit("Move_Python", False)
                    self.state = PLCState.MOVE_PLACE

        elif self.state == PLCState.MOVE_PLACE:
            if get_bit("On_Position_PLC"):
                self.state = PLCState.DONE

        elif self.state == PLCState.DONE:
            set_bit("Start_Python", False)
