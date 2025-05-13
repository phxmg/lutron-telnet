#!/usr/bin/env python3
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from lutron_quick import LutronQuick

# Master Bedroom Bay Window Light zone is ID 10
MASTER_BEDROOM_LIGHT_ZONE = 10

# Replace with your bridge IP address
BRIDGE_IP = "192.168.1.100"

def main():
    # Create Lutron controller instance
    controller = LutronQuick(BRIDGE_IP)
    
    if not controller.connect():
        print("Failed to connect to the bridge")
        return
    
    try:
        # Example control sequence
        print("Turning on Bay Window Lights...")
        controller.set_light(MASTER_BEDROOM_LIGHT_ZONE, 100)  # 100% brightness
        time.sleep(2)
        
        print("Setting to 50% brightness...")
        controller.set_light(MASTER_BEDROOM_LIGHT_ZONE, 50)  # 50% brightness
        time.sleep(2)
        
        print("Turning off lights...")
        controller.set_light(MASTER_BEDROOM_LIGHT_ZONE, 0)  # Off
    finally:
        controller.close()
        print("Connection closed")

if __name__ == "__main__":
    main() 