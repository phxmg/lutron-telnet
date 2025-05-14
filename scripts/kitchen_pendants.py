#!/usr/bin/env python3
"""
Kitchen Pendants - Control kitchen island pendant lights
"""
import argparse
import sys
from src.lutron_controller import LutronController
from src.lutron_zones import KITCHEN

# Hardcoded bridge IP address
DEFAULT_BRIDGE_IP = "192.168.49.91"

def parse_args():
    parser = argparse.ArgumentParser(description='Control Kitchen Island Pendant Lights')
    parser.add_argument('--ip', '-i', default=DEFAULT_BRIDGE_IP, 
                        help=f'IP address of the Lutron bridge (default: {DEFAULT_BRIDGE_IP})')
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True
    
    # ON command
    subparsers.add_parser('on', help='Turn pendant lights ON')
    
    # OFF command
    subparsers.add_parser('off', help='Turn pendant lights OFF')
    
    # Set to 50% command
    subparsers.add_parser('half', help='Set pendant lights to 50% brightness')
    
    # SET command
    set_parser = subparsers.add_parser('set', help='Set pendant lights to specific level')
    set_parser.add_argument('--level', '-l', type=float, required=True, 
                         help='Brightness level (0.0-100.0)')
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Create controller and connect
    with LutronController(args.ip) as controller:
        if not controller.connected:
            print("Failed to connect to the bridge")
            return 1
        
        # Get the pendant light info
        pendant = KITCHEN["PENDANTS"]
        zone_id = pendant["id"]
        name = pendant["name"]
        
        # Determine the brightness level based on command
        if args.command == 'on':
            print(f"Turning {name} ON")
            level = 100.0
        elif args.command == 'off':
            print(f"Turning {name} OFF")
            level = 0.0
        elif args.command == 'half':
            print(f"Setting {name} to 50%")
            level = 50.0
        elif args.command == 'set':
            level = max(0.0, min(100.0, args.level))
            print(f"Setting {name} to {level}%")
        
        # Control the light
        controller.set_light(zone_id, level)
        return 0

if __name__ == "__main__":
    sys.exit(main()) 