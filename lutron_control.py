#!/usr/bin/env python3
import argparse
import sys
from src.lutron_quick import LutronQuick

def parse_args():
    parser = argparse.ArgumentParser(description='Control Lutron Caseta devices via Telnet')
    parser.add_argument('--ip', '-i', required=True, help='IP address of the Lutron bridge')
    parser.add_argument('--zone', '-z', type=int, required=True, help='Zone ID to control')
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True
    
    # ON command
    subparsers.add_parser('on', help='Turn zone ON')
    
    # OFF command
    subparsers.add_parser('off', help='Turn zone OFF')
    
    # SET command
    set_parser = subparsers.add_parser('set', help='Set zone to specific level')
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
            print(f"Turning zone {args.zone} ON")
            controller.set_light(args.zone, 100.0)
        elif args.command == 'off':
            print(f"Turning zone {args.zone} OFF")
            controller.set_light(args.zone, 0.0)
        elif args.command == 'set':
            level = max(0.0, min(100.0, args.level))
            print(f"Setting zone {args.zone} to {level}%")
            controller.set_light(args.zone, level)
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        controller.close()

if __name__ == "__main__":
    sys.exit(main()) 