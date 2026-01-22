plcIpadress = ['192.168.10.1', 0, 1]  # IP, Rack, Slot
topButtons = ['Home', 'Settings', 'Log', 'test','control PLC']
testButtons = ['Forward X', 'Backward X', 'Forward Y', 'Backward Y', 'Forward Z', 'Backward Z', 'X coord', 'Y coord', 'Z coord','Set Speed X', 'Set Speed Y', 'Set Speed Z', 'Emergency Stop']
testButtonsV1 = ['Send Bool', 'Receive Bool', 'Send Int', 'Receive Int', 'Send Float', 'Receive Float', 'Send String', 'Receive String', 'Send Lreal', 'Receive Lreal']
lampColors = ['Green', 'Yellow', 'Red']
steps = 3
motors = ["X-motor", "Y-motor", "Z-motor"]
devices = [*motors, "Gripper", "Camera", 'X-endstop', 'Y-endstop', 'Z-endstop']