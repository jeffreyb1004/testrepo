import time
import tkinter as tk
from dynamixel_sdk import *    # Dynamixel SDK
from tkinter import messagebox

# Control table addresses
ADDR_TORQUE_ENABLE      = 64
ADDR_GOAL_POSITION      = 116
ADDR_PRESENT_POSITION   = 132

# Protocol version
PROTOCOL_VERSION        = 2.0

# Default settings
DXL_ID_1                = 1                 # Dynamixel ID for first motor
DXL_ID_2                = 2                 # Dynamixel ID for second motor
BAUDRATE                = 57600             # Dynamixel baudrate
DEVICENAME              = 'COM3'             # <- Change this to match your port!

TORQUE_ENABLE           = 1
TORQUE_DISABLE          = 0

# Goal positions
DXL_MINIMUM_POSITION_VALUE  = 1000
DXL_MAXIMUM_POSITION_VALUE  = 3000

# Initialize PortHandler and PacketHandler
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    messagebox.showerror("Error", "Failed to open the port!")
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    messagebox.showerror("Error", "Failed to change the baudrate!")
    quit()

# Enable Dynamixel Torque for both motors
def enable_torque(dxl_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        messagebox.showerror("Error", f"Comm error: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        messagebox.showerror("Error", f"Dynamixel error: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        print(f"Dynamixel {dxl_id} has been successfully connected and torque enabled")

# Enable torque for both motors
enable_torque(DXL_ID_1)
enable_torque(DXL_ID_2)

# Function to read current position
def read_position(dxl_id):
    dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(portHandler, dxl_id, ADDR_PRESENT_POSITION)

    if dxl_comm_result != COMM_SUCCESS:
        print(f"Comm error: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Dynamixel error: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        return dxl_present_position

# Function to move motor 1 (up +100, down -100)
def move_motor_1(direction):
    current_position = read_position(DXL_ID_1)
    if current_position is not None:
        if direction == 'up':
            new_goal_position = current_position + 100  # Move 100 steps forward
        elif direction == 'down':
            new_goal_position = current_position - 100  # Move 100 steps backward
        packetHandler.write4ByteTxRx(portHandler, DXL_ID_1, ADDR_GOAL_POSITION, new_goal_position)
        print(f"Motor 1 moved to position: {new_goal_position}")

# Function to move motor 2 (left +100, right -100)
def move_motor_2(direction):
    current_position = read_position(DXL_ID_2)
    if current_position is not None:
        if direction == 'left':
            new_goal_position = current_position + 100  # Move 100 steps forward (left)
        elif direction == 'right':
            new_goal_position = current_position - 100  # Move 100 steps backward (right)
        packetHandler.write4ByteTxRx(portHandler, DXL_ID_2, ADDR_GOAL_POSITION, new_goal_position)
        print(f"Motor 2 moved to position: {new_goal_position}")

# Create the Tkinter window
root = tk.Tk()
root.title("Dynamixel Motor Control")

# Function to handle key presses for motor movement
def on_key_press(event):
    if event.keysym == 'Up':   # Move motor 1 up
        move_motor_1('up')
    elif event.keysym == 'Down':  # Move motor 1 down
        move_motor_1('down')
    elif event.keysym == 'Left':  # Move motor 2 left
        move_motor_2('left')
    elif event.keysym == 'Right':  # Move motor 2 right
        move_motor_2('right')

# Bind arrow keys to the Tkinter window
root.bind("<KeyPress>", on_key_press)

# Function to cleanly close connection when closing the window
def on_closing():
    # Disable Torque for both motors
    packetHandler.write1ByteTxRx(portHandler, DXL_ID_1, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    packetHandler.write1ByteTxRx(portHandler, DXL_ID_2, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)

    # Close port
    portHandler.closePort()
    print("Connection closed")
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the Tkinter event loop
root.mainloop()
