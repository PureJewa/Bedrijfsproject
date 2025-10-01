import snap7
from logger import write_log
from snap7.util import get_bool, set_bool


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
def sendData(client, db_number, start, size):
    data = client.db_read(1, 0, 1)
    bit0 = get_bool(data, 0, 0)  # DB1.DBX0.0
    bit1 = get_bool(data, 0, 1)  # DB1.DBX0.1
    #
    # # Print the states of the bits
    print("DB1.DBX0.0:", bit0)
    print("DB1.DBX0.1:", bit1)
    #
    # # Set DB1.DBX0.0 to True (high)
    set_bool(data, 0, 0, True)
    #
    # # Write the modified byte back to the PLC
    client.db_write(1, 0, data)
    # try:
    #     if not client.get_connected():
    #         write_log("PLC not connected. Attempting to reconnect...")
    #         client.connect(client.get_ip(), client.get_rack(), client.get_slot())
    #         if not client.get_connected():
    #             write_log("Reconnection failed.")
    #             return
    #     data = client.db_read(db_number, start, size)
    #     set_bool(data, 0, 0, True)
    #     client.db_write(db_number, start, data)
    # except Exception as e:
    #     write_log(f"Error sending data to PLC: {e}")
def receiveData(client, db_number, start, size):
    try:
        if not client.get_connected():
            write_log("PLC not connected. Attempting to reconnect...")
            client.connect(client.get_ip(), client.get_rack(), client.get_slot())
            if not client.get_connected():
                write_log("Reconnection failed.")
                return None
    except Exception as e:
        write_log(f"Error receiving data from PLC: {e}")
        return None
    return client.db_read(db_number, start, size)