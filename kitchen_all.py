#!/usr/bin/env python3
import argparse
import json
import sys
import time
import threading
from src.lutron_quick import LutronQuick

# Hardcoded bridge IP address
DEFAULT_BRIDGE_IP = "192.168.49.91"

# Hardcoded kitchen zone IDs
KITCHEN_ZONES = [
    {"id": 27, "name": "Sink Light"},
    {"id": 30, "name": "Island Pendants"},
    {"id": 31, "name": "Island Lights"},
    {"id": 33, "name": "Main Lights"}
]

def parse_args():
    parser = argparse.ArgumentParser(description='Control all Kitchen lights')
    parser.add_argument('--ip', '-i', default=DEFAULT_BRIDGE_IP, 
                        help=f'IP address of the Lutron bridge (default: {DEFAULT_BRIDGE_IP})')
    parser.add_argument('--mode', '-m', choices=['sequential', 'batch'], default='batch',
                        help='Control mode: sequential (one by one) or batch (all at once)')
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    subparsers.required = True
    
    # LIST command
    subparsers.add_parser('list', help='List all kitchen lights')
    
    # ON command
    subparsers.add_parser('on', help='Turn all kitchen lights ON')
    
    # OFF command
    subparsers.add_parser('off', help='Turn all kitchen lights OFF')
    
    # Set to 50% command
    subparsers.add_parser('half', help='Set all kitchen lights to 50% brightness')
    
    # SET command
    set_parser = subparsers.add_parser('set', help='Set all kitchen lights to specific level')
    set_parser.add_argument('--level', '-l', type=float, required=True, 
                         help='Brightness level (0.0-100.0)')
    
    return parser.parse_args()

def list_kitchen_lights():
    print("\nKitchen Lights:\n")
    print("-" * 30)
    
    for zone in KITCHEN_ZONES:
        print(f"  Zone {zone['id']:>2}: {zone['name']}")
    
    print("")

def set_light_thread(controller, zone_id, level):
    """Function for controlling a light in its own thread"""
    controller.set_light(zone_id, level)

def set_all_lights_sequential(controller, level):
    """Set all lights one by one, waiting for each to complete"""
    level = max(0.0, min(100.0, level))
    print(f"Setting all kitchen lights to {level}% (sequential mode)")
    
    # Control each zone sequentially
    for zone in KITCHEN_ZONES:
        print(f"  - Setting {zone['name']} (Zone {zone['id']}) to {level}%")
        controller.set_light(zone['id'], level)
        time.sleep(0.5)  # Short delay between commands for stability

def set_all_lights_batch(controller, level):
    """Set all lights simultaneously using threads"""
    level = max(0.0, min(100.0, level))
    print(f"Setting all kitchen lights to {level}% (batch mode)")
    
    # Create a thread for each light
    threads = []
    for zone in KITCHEN_ZONES:
        print(f"  - Queuing {zone['name']} (Zone {zone['id']})")
        thread = threading.Thread(
            target=set_light_thread,
            args=(controller, zone['id'], level)
        )
        threads.append(thread)
    
    # Start all threads (sends commands in parallel)
    for thread in threads:
        thread.start()
        # Small stagger to avoid flooding the bridge
        time.sleep(0.1)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

def main():
    args = parse_args()
    
    # Just list the lights if requested
    if args.command == 'list':
        list_kitchen_lights()
        return 0
    
    # Otherwise, control the lights
    controller = LutronQuick(args.ip)
    
    if not controller.connect():
        print("Failed to connect to the bridge")
        return 1
    
    try:
        # Determine the brightness level based on command
        if args.command == 'on':
            level = 100.0
        elif args.command == 'off':
            level = 0.0
        elif args.command == 'half':
            level = 50.0
        elif args.command == 'set':
            level = args.level
        
        # Use the appropriate control method based on mode
        if args.mode == 'sequential':
            set_all_lights_sequential(controller, level)
        else:  # batch mode
            set_all_lights_batch(controller, level)
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        controller.close()
        print("Connection closed")

if __name__ == "__main__":
    sys.exit(main()) 