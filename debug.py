#!/usr/bin/env python3

from lutron_client import LutronBridge

# Create the bridge connection
bridge = LutronBridge("192.168.49.91")

try:
    # Connect to the bridge
    if bridge.connect():
        print("\n--- Raw Responses ---")
        
        # Get raw area response
        print("\nAREA Command:")
        area_response = bridge.send_command("?AREA")
        print(repr(area_response))
        
        # Get raw zone response
        print("\nZONE Command:")
        zone_response = bridge.send_command("?ZONE")
        print(repr(zone_response))
        
        # Get raw output response
        print("\nOUTPUT Command:")
        output_response = bridge.send_command("?OUTPUT")
        print(repr(output_response))
        
        # Get raw device response
        print("\nDEVICE Command:")
        device_response = bridge.send_command("?DEVICE")
        print(repr(device_response))
        
        print("\n--- End of Responses ---")
except Exception as e:
    print(f"Error: {e}")
finally:
    bridge.close()
    print("\nConnection closed") 