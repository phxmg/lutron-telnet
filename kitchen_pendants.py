#!/usr/bin/env python3
import argparse
import sys
from src.lutron_quick import LutronQuick

# Hardcoded zone ID for Kitchen Island Pendants
PENDANT_LIGHT_ZONE = 30

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
    
    # Create controller instance
    controller = LutronQuick(args.ip)
    
    if not controller.connect():
        print("Failed to connect to the bridge")
        return 1
    
    try:
        if args.command == 'on':
            print("Turning kitchen pendant lights ON")
            controller.set_light(PENDANT_LIGHT_ZONE, 100.0)
        elif args.command == 'off':
            print("Turning kitchen pendant lights OFF")
            controller.set_light(PENDANT_LIGHT_ZONE, 0.0)
        elif args.command == 'half':
            print("Setting kitchen pendant lights to 50%")
            controller.set_light(PENDANT_LIGHT_ZONE, 50.0)
        elif args.command == 'set':
            level = max(0.0, min(100.0, args.level))
            print(f"Setting kitchen pendant lights to {level}%")
            controller.set_light(PENDANT_LIGHT_ZONE, level)
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        controller.close()

if __name__ == "__main__":
    sys.exit(main()) 