# communicationTia.py
# Module for communicating with a Siemens PLC using snap7

import struct
import snap7
from snap7.util import *
from Python_code.Communication.communicationConfig import *
from Python_code.Logger.logger import write_log

# Make a global snap7 client
client = snap7.client.Client()


def plc_addr(addr):
    """
    Unpack a PLC address tuple like (db, byte, bit).
    :param addr: Tuple containing (db, byte, bit)
    :return: db, byte, bit
    """
    try:
        db, byte, bit = addr
        return db, byte, bit
    except Exception:
        raise ValueError(f"Invalid PLC address format: {addr}")


def plc_connect():
    """
    Make a connection to the PLC.
    """
    try:
        write_log("Attempting to connect to PLC")
        if not client.get_connected():
            client.connect(PLC_IP, RACK, SLOT)
        return True
    except Exception as e:
        write_log(e)
        return False


def plc_disconnect():
    """
    Disconnect from the PLC.
    """
    try:
        if client.get_connected():
            client.disconnect()
            write_log("Disconnected from PLC.")
    except Exception as e:
        write_log(e)
        pass


def set_bit(name: str, value: bool):
    """
    Set a bit in the PLC data block by name.
    :param name: Assigned name of the bit in communicationConfig.BITS_ALL
    :param value: True or False to set the bit
    """
    try:
        byte_index, bit_index = BITS_ALL[name]
        data = bytearray(client.db_read(DB_NUM, byte_index, 1))
        set_bool(data, 0, bit_index, bool(value))
        client.db_write(DB_NUM, byte_index, data)
        write_log(f"Wrote BOOL, {name} at DB{DB_NUM}.{byte_index}.{bit_index}: {value}")
    except Exception as e:
        write_log(f"Error setting bit {e}, name: {name}, value: {value}")


def get_bit(name: str) -> bool:
    """
    Get a bit from the PLC data block by name.
    :param name: Assigned name of the bit in communicationConfig.BITS_ALL
    :return: Boolean value of the bit
    """
    try:
        byte_index, bit_index = BITS_ALL[name]
        raw = client.db_read(DB_NUM, byte_index, 1)
        byte = raw[0]
        write_log(f"Read BOOL, {name} at DB{DB_NUM}.{byte_index}.{bit_index}: {bool((byte >> bit_index) & 0x01)}")
        return bool((byte >> bit_index) & 0x01)
    except Exception as e:
        write_log(f"Error getting bit {e}")
        return False


def write_lreal(byte_index: str, value: float):
    """
    Write a LREAL (double-precision float) to the PLC data block.
    :param byte_index: Assigned byte index in communicationConfig.LREAL_OFFSETS
    :param value: Value to write to the PLC
    """
    try:
        write_log(f"Writing LREAL at DB{DB_NUM}.{byte_index}: {value}")
        b = struct.pack(">d", float(value))  # S7 big-endian
        client.db_write(DB_NUM, byte_index, b)
    except Exception as e:
        write_log(e)


def read_lreal(byte_index: int) -> float:
    """
    Read a LREAL (double-precision float) from the PLC data block.
    :param byte_index: Assigned byte index in communicationConfig.LREAL_OFFSETS
    :return: Value read from the PLC
    """
    try:
        write_log(f"Reading LREAL from DB{DB_NUM}.{byte_index}")
        b = client.db_read(DB_NUM, byte_index, 8)
        return struct.unpack(">d", b)[0]
    except Exception as e:
        write_log(e)


def write_int(byte_index: int, value: int):
    """
    Write an INT (16-bit integer) to the PLC data block.
    :param byte_index: Assigned byte index in communicationConfig.INT_OFFSETS
    :param value: Value to write to the PLC
    """
    try:
        write_log(f"Writing INT at DB{DB_NUM}.{byte_index}: {value}")
        b = struct.pack(">h", int(value))  # S7 big-endian
        client.db_write(DB_NUM, byte_index, b)
    except Exception as e:
        write_log(e)


def read_int(byte_index: int) -> int:
    """
    Read an INT (16-bit integer) from the PLC data block.
    :param byte_index: Assigned byte index in communicationConfig.INT_OFFSETS
    :return: Value read from the PLC
    """
    try:
        write_log(f"Reading INT from DB{DB_NUM}.{byte_index}")
        b = client.db_read(DB_NUM, byte_index, 2)
        return struct.unpack(">h", b)[0]
    except Exception as e:
        write_log(e)

