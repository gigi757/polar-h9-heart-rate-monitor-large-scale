import asyncio
import tkinter as tk
from bleak import BleakClient

# Replace with your Polar H9's address
POLAR_H9_ADDRESS = "A0:9E:1A:E0:4C:A3"  # Replace with your device's address

# UUIDs for Heart Rate Service and Characteristic
HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Global variable to store the heart rate
heart_rate = 0

# Function to parse heart rate data
def parse_heart_rate_data(data):
    byte0 = data[0]
    flags = byte0 & 0x01  # Check if heart rate is 8-bit or 16-bit
    return data[1] if flags == 0 else int.from_bytes(data[1:3], byteorder="little")

# Callback function to handle heart rate notifications
def heart_rate_notification_handler(sender, data):
    global heart_rate
    heart_rate = parse_heart_rate_data(data)

# Function to update the GUI with the latest heart rate
def update_gui():
    heart_rate_label.config(text=f"{heart_rate}")
    root.after(100, update_gui)  # Update the GUI every 100ms

# Function to connect to the Polar H9
async def connect_to_polar_h9():
    print(f"Connecting to Polar H9 at {POLAR_H9_ADDRESS}...")
    async with BleakClient(POLAR_H9_ADDRESS) as client:
        print("Connected!")

        # Enable notifications for heart rate data
        await client.start_notify(HEART_RATE_MEASUREMENT_CHAR_UUID, heart_rate_notification_handler)
        print("Listening for heart rate data...")

        # Keep the connection alive
        while True:
            await asyncio.sleep(1)

# Create the main Tkinter window
root = tk.Tk()
root.title("Polar H9 Heart Rate Monitor")
root.attributes("-fullscreen", True)  # Make the window full-screen

# Create a label to display the heart rate
heart_rate_label = tk.Label(root, text="0", font=("Arial", 400), fg="red")
heart_rate_label.pack(expand=True)

# Start updating the GUI
update_gui()

# Run the asyncio event loop and Tkinter main loop together
async def main():
    await connect_to_polar_h9()

# Start the asyncio task and Tkinter main loop
import threading
threading.Thread(target=asyncio.run, args=(main(),), daemon=True).start()
root.mainloop()
