#!/usr/bin/env python3

import argparse
from lutron_client import LutronBridge

def control_light(bridge, zone_id, level):
    """
    Control a light by setting its level.
    
    Args:
        bridge (LutronBridge): Connected bridge instance
        zone_id (str): Zone ID to control
        level (float): Light level (0.0 to 100.0)
    
    Returns:
        str: Response from bridge
    """
    # Ensure level is within bounds
    level = max(0.0, min(100.0, level))
    
    # Lutron expects levels between 0.0 and 100.0
    command = f"#OUTPUT,{zone_id},1,{level}"
    response = bridge.send_command(command)
    return response

def main():
    parser = argparse.ArgumentParser(description='Control Lutron Caseta devices')
    parser.add_argument('--ip', default='192.168.49.91', help='Bridge IP address')
    parser.add_argument('--list', action='store_true', help='List all controllable entities')
    parser.add_argument('--zone', type=str, help='Zone ID to control')
    parser.add_argument('--level', type=float, help='Light level (0.0 to 100.0)')
    
    args = parser.parse_args()
    
    bridge = LutronBridge(args.ip)
    
    try:
        if bridge.connect():
            if args.list:
                # List all entities
                entities = bridge.get_controllable_entities()
                from lutron_client import print_entities
                print_entities(entities)
            elif args.zone is not None and args.level is not None:
                # Control a specific zone
                response = control_light(bridge, args.zone, args.level)
                print(f"Command sent to zone {args.zone}. Response: {response}")
            else:
                # Default behavior - list entities
                print("No action specified. Use --list to list entities or --zone and --level to control a device.")
                entities = bridge.get_controllable_entities()
                from lutron_client import print_entities
                print_entities(entities)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        bridge.close()
        print("\nConnection closed")

if __name__ == "__main__":
    main() 