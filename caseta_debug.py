#!/usr/bin/env python3

from lutron_client import LutronBridge
import time

# Create the bridge connection
bridge = LutronBridge("192.168.49.91")

try:
    # Connect to the bridge
    if bridge.connect():
        print("\nTesting different command formats for Caseta...")
        
        # Try integration report commands (used with some Caseta models)
        print("\n--- Integration Report Commands ---")
        
        # Request device names and types
        print("\nDevice Listing:")
        response = bridge.send_command("?DEVICE,1,3")
        print(response)
        
        # Try retrieving device status
        print("\nDevice Status:")
        response = bridge.send_command("?DEVICE,1,6")
        print(response)
        
        # Try direct monitoring commands
        print("\n--- Direct Monitoring Commands ---")
        
        # Listen for events briefly
        print("Monitoring for 5 seconds...")
        start_time = time.time()
        while time.time() - start_time < 5:
            try:
                if bridge.socket:
                    bridge.socket.settimeout(1)
                    data = bridge.socket.recv(4096)
                    if data:
                        print(f"Received: {data}")
            except Exception as e:
                pass  # Ignore timeouts during monitoring
        
        # Try button press simulation command for debugging
        print("\n--- Button Press Simulation ---")
        response = bridge.send_command("#DEVICE,1,1")
        print(response)
        
        # Try some known working Caseta-specific commands
        print("\n--- Caseta-Specific Commands ---")
        
        # Query bridge info
        print("\nBridge Info:")
        response = bridge.send_command("?SYSTEM")
        print(response)
        
        # For Smart Bridge Pro, try a scenes query
        print("\nScenes Query:")
        response = bridge.send_command("?SCENE")
        print(response)
        
        print("\n--- End of Tests ---")
except Exception as e:
    print(f"Error: {e}")
finally:
    bridge.close()
    print("\nConnection closed") 