import snap7
from logger import write_log
from snap7.util import get_bool, set_bool, get_int, set_int, get_real, set_real, get_string, set_string, set_lreal, get_lreal

startPLC = (1, 0, 1)  # DB, start, size
pausePLC = (1, 1, 1)  # DB, start, size
stopPLC = (1, 2, 1)   # DB, start, size

speedPLC = (2, 0)
accelerationPLC = (2, 2)
cyclesPLC = (2, 4)
# client = snap7.client.Client()
# client.connect('192.168.10.1', 0, 1)  # IP, Rack, Slot
#
# # Read 1 byte (DB1, byte offset 0)
# data = client.db_read(1, 0, 1)
#
# # Extract bits from that byte
# bit0 = get_bool(data, 0, 0)  # DB1.DBX0.0
# bit1 = get_bool(data, 0, 1)  # DB1.DBX0.1
#
# # Print the states of the bits
# print("DB1.DBX0.0:", bit0)
# print("DB1.DBX0.1:", bit1)
#
# # Set DB1.DBX0.0 to True (high)
# set_bool(data, 0, 0, True)
#
# # Write the modified byte back to the PLC
# client.db_write(1, 0, data)
#
# # Verify the change by reading the byte again
# data = client.db_read(1, 0, 1)
# bit0 = get_bool(data, 0, 0)  # DB1.DBX0.0
# print("DB1.DBX0.0 after setting high:", bit0)

def TIAConnection(ip, rack, slot):
    try:
        client = snap7.client.Client()
        client.connect(ip, rack, slot)
        if client.get_connected():
            write_log(f"Connected to PLC at {ip} (Rack: {rack}, Slot: {slot})")
        return client
    except Exception as e:
        write_log(f"Connection error: {e}")
        return None
# def sendData(client, db_number, start, size):
#     data = client.db_read(1, 0, 1)
#     bit0 = get_bool(data, 0, 0)  # DB1.DBX0.0
#     bit1 = get_bool(data, 0, 1)  # DB1.DBX0.1
#     #
#     # # Print the states of the bits
#     print("DB1.DBX0.0:", bit0)
#     print("DB1.DBX0.1:", bit1)
#     #
#     # # Set DB1.DBX0.0 to True (high)
#     set_bool(data, 0, 0, True)
#     #
#     # # Write the modified byte back to the PLC
#     client.db_write(1, 0, data)
#
# def sendBool(client, db_number, start, size, flag):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return
#         data = client.db_read(db_number, start, size)
#         set_bool(data, start, size, flag)
#         client.db_write(db_number, start, data)
#     except Exception as e:
#         write_log(f"Error sending bool data to PLC: {e}")
# def receiveBool(client, db_number, start, size):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return None
#         data = client.db_read(db_number, start, 1)
#         bit = get_bool(data, start, size)
#         return bit
#     except Exception as e:
#         write_log(f"Error receiving data from PLC: {e}")
#         return None
# def sendInt(client, db_number, start, value):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return
#         # 2 bytes voor INT
#         data = bytearray(2)
#         set_int(data, 0, value)
#         client.db_write(db_number, start, data)
#     except Exception as e:
#         write_log(f"Error sending int data to PLC: {e}")
#
# def receiveInt(client, db_number, start):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return None
#         data = client.db_read(db_number, start, 2)  # 2 bytes voor INT
#         return get_int(data, 0)
#     except Exception as e:
#         write_log(f"Error receiving int data from PLC: {e}")
#         return None
# def sendFloat(client, db_number, start, value):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return
#         data = bytearray(4)
#         set_real(data, 0, value)
#         client.db_write(db_number, start, data)
#     except Exception as e:
#         write_log(f"Error sending float data to PLC: {e}")
#
# def receiveFloat(client, db_number, start):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return None
#         data = client.db_read(db_number, start, 4)  # 4 bytes voor REAL
#         return get_real(data, 0)
#     except Exception as e:
#         write_log(f"Error receiving float data from PLC: {e}")
#         return None
# def sendString(client, db_number, start, value, max_length=20):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return
#
#         data = bytearray(max_length + 2)
#         set_string(data, 0, value, max_length)
#         client.db_write(db_number, start, data)
#     except Exception as e:
#         write_log(f"Error sending string data to PLC: {e}")
#
# def receiveString(client, db_number, start, max_length=20):
#     try:
#         if not client.get_connected():
#             write_log("PLC not connected. Attempting to reconnect...")
#             client.connect(client.get_ip(), client.get_rack(), client.get_slot())
#             if not client.get_connected():
#                 write_log("Reconnection failed.")
#                 return None
#
#         data = client.db_read(db_number, start, max_length + 2)
#         return get_string(data, 0, max_length)
#     except Exception as e:
#         write_log(f"Error receiving string data from PLC: {e}")
#         return None
# ----------------------------------------
# Functions to communicate with a PLC (Siemens)
# We can send and receive different types of data: BOOL, INT, FLOAT, STRING
# ----------------------------------------

# --- Send a single boolean (True/False) to the PLC ---
def sendBool(client, db_number, start, size, flag):
    try:
        # Check if we are connected to the PLC
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())  # Try to reconnect
            if not client.get_connected():
                write_log("Reconnection failed.")
                return

        # Read the current data block from PLC
        data = client.db_read(db_number, start, size)

        # Set the specific bit to True or False
        set_bool(data, start, size, flag)

        # Write the updated data back to the PLC
        client.db_write(db_number, start, data)

    except Exception as e:
        write_log(f"Error sending bool data to PLC: {e}")  # Log any errors


# --- Receive a single boolean (True/False) from the PLC ---
def receiveBool(client, db_number, start, size):
    try:
        # Check connection
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return None

        # Read the data block from PLC (1 byte for a single BOOL)
        data = client.db_read(db_number, start, 1)

        # Extract the boolean value
        bit = get_bool(data, start, size)
        return bit

    except Exception as e:
        write_log(f"Error receiving data from PLC: {e}")
        return None


# --- Send a 16-bit integer to the PLC ---
def sendInt(client, db_number, start, value):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return

        # INT = 2 bytes (16 bits)
        data = bytearray(2)

        # Convert the integer into bytes and store in data
        set_int(data, 0, value)

        # Write the data block to the PLC
        client.db_write(db_number, start, data)

    except Exception as e:
        write_log(f"Error sending int data to PLC: {e}")


# --- Receive a 16-bit integer from the PLC ---
def receiveInt(client, db_number, start):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return None

        # Read 2 bytes from PLC
        data = client.db_read(db_number, start, 2)
        return get_int(data, 0)  # Convert bytes back to integer

    except Exception as e:
        write_log(f"Error receiving int data from PLC: {e}")
        return None


# --- Send a 32-bit floating point number (REAL) to the PLC ---
def sendFloat(client, db_number, start, value):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return

        # REAL = 4 bytes
        data = bytearray(4)

        # Convert the float into bytes and store in data
        set_real(data, 0, value)

        # Write to PLC
        client.db_write(db_number, start, data)

    except Exception as e:
        write_log(f"Error sending float data to PLC: {e}")


# --- Receive a 32-bit floating point number from the PLC ---
def receiveFloat(client, db_number, start):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return None

        # Read 4 bytes from PLC (REAL)
        data = client.db_read(db_number, start, 4)
        return get_real(data, 0)  # Convert bytes to float

    except Exception as e:
        write_log(f"Error receiving float data from PLC: {e}")
        return None


# --- Send a string (text) to the PLC ---
def sendString(client, db_number, start, value, max_length=20):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return

        # Create a byte array: max_length + 2 bytes for string header
        data = bytearray(max_length + 2)

        # Convert the string into bytes and store in data
        set_string(data, 0, value, max_length)

        # Write to PLC
        client.db_write(db_number, start, data)

    except Exception as e:
        write_log(f"Error sending string data to PLC: {e}")


# --- Receive a string (text) from the PLC ---
def receiveString(client, db_number, start, max_length=20):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return None

        # Read bytes from PLC (max_length + 2 for string header)
        data = client.db_read(db_number, start, max_length + 2)

        # Convert bytes to string
        return get_string(data, 0, max_length)

    except Exception as e:
        write_log(f"Error receiving string data from PLC: {e}")
        return None

def sendLreal(client, db_number, start, value):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return

        # LREAL = 8 bytes
        data = bytearray(8)

        # Convert the float into bytes and store in data
        set_lreal(data, 0, value)

        # Write to PLC
        client.db_write(db_number, start, data)

    except Exception as e:
        write_log(f"Error sending Lreal data to PLC: {e}")

def recieveLreal(client, db_number, start):
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
