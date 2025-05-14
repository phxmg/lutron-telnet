#!/usr/bin/env python3
"""
Lights - Control any list of lights by zone ID
"""
import argparse
import sys
from src.lutron_controller import LutronController

# Hardcoded bridge IP address
DEFAULT_BRIDGE_IP = "192.168.49.91"

def parse_args():
    parser = argparse.ArgumentParser(description='Control multiple Lutron light zones')
    parser.add_argument('--ip', '-i', default=DEFAULT_BRIDGE_IP, 
                        help=f'IP address of the Lutron bridge (default: {DEFAULT_BRIDGE_IP})')
    parser.add_argument('--zones', '-z', type=int, nargs='+', required=True,
                        help='One or more zone IDs to control (e.g., -z 10 27 30)')
    parser.add_argument('--mode', '-m', choices=['sequential', 'batch'], default='batch',
                        help='Control mode: sequential (one by one) or batch (all at once)')
    parser.add_argument('--delay', '-d', type=float, default=0.5,
                        help='Delay between commands in sequential mode (seconds, default: 0.5)')
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True
    
    # ON command
    subparsers.add_parser('on', help='Turn lights ON')
    
    # OFF command
    subparsers.add_parser('off', help='Turn lights OFF')
    
    # Set to 50% command
    subparsers.add_parser('half', help='Set lights to 50% brightness')
    
    # SET command
    set_parser = subparsers.add_parser('set', help='Set lights to specific level')
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
        
        # Determine the brightness level based on command
        if args.command == 'on':
            level = 100.0
        elif args.command == 'off':
            level = 0.0
        elif args.command == 'half':
            level = 50.0
        elif args.command == 'set':
            level = args.level
        
        # Print summary
        zone_str = ", ".join(str(z) for z in args.zones)
        print(f"Controlling zones: {zone_str}")
        
        # Use the appropriate control method based on mode
        if args.mode == 'sequential':
            controller.set_lights_sequential(args.zones, level, args.delay)
        else:  # batch mode
            controller.set_lights_batch(args.zones, level)
        
        return 0

if __name__ == "__main__":
    sys.exit(main()) 