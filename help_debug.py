#!/usr/bin/env python3

from lutron_client import LutronBridge

# Create the bridge connection
bridge = LutronBridge("192.168.49.91")

try:
    # Connect to the bridge
    if bridge.connect():
        print("\n--- Help Command Response ---")
        help_response = bridge.send_command("HELP")
        print(help_response)
        
        # Try a different version of help
        print("\n--- ? Command Response ---")
        q_response = bridge.send_command("?")
        print(q_response)
        
        # Try interrogating the system version
        print("\n--- Version Command Response ---")
        version_response = bridge.send_command("#SYSTEM,1,?VERSION")
        print(version_response)
        
        print("\n--- End of Responses ---")
except Exception as e:
    print(f"Error: {e}")
finally:
    bridge.close()
    print("\nConnection closed") 