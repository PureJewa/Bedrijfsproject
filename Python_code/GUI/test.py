import snap7
from snap7.util import get_bool, set_bool

client = snap7.client.Client()
client.connect('192.168.10.1', 0, 1)  # IP, Rack, Slot

# Read 1 byte (DB1, byte offset 0)
data = client.db_read(1, 0, 1)

# Extract bits from that byte
bit0 = get_bool(data, 0, 0)  # DB1.DBX0.0
bit1 = get_bool(data, 0, 1)  # DB1.DBX0.1

# Print the states of the bits
print("DB1.DBX0.0:", bit0)
print("DB1.DBX0.1:", bit1)

# Set DB1.DBX0.0 to True (high)
set_bool(data, 0, 0, True)

# Write the modified byte back to the PLC
client.db_write(1, 0, data)

# Verify the change by reading the byte again
data = client.db_read(1, 0, 1)
bit0 = get_bool(data, 0, 0)  # DB1.DBX0.0
print("DB1.DBX0.0 after setting high:", bit0)
