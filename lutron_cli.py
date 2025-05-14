#!/usr/bin/env python3
"""
Lutron Command Line Interface - Unified CLI for all Lutron operations
"""
import argparse
import sys
import time
from src.lutron_controller import LutronController
from src.lutron_zones import (
    KITCHEN, KITCHEN_ALL, MASTER_BEDROOM, 
    get_zone_names, print_zones
)

# Hardcoded bridge IP address
DEFAULT_BRIDGE_IP = "192.168.49.91"

def parse_args():
    """Parse command line arguments for the unified CLI"""
    # Create the main parser
    parser = argparse.ArgumentParser(
        description='Lutron Caseta Telnet Controller CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Control a specific zone
  ./lutron_cli.py zone --zone-id 10 on
  ./lutron_cli.py zone --zone-id 30 off
  ./lutron_cli.py zone --zone-id 27 set --level 50
  
  # Control a room
  ./lutron_cli.py room kitchen on
  ./lutron_cli.py room bedroom off
  
  # Run a light show
  ./lutron_cli.py show kitchen-standard
  ./lutron_cli.py show kitchen-optimized
  
  # Run the party mode
  ./lutron_cli.py party
  
  # Monitor bridge activity
  ./lutron_cli.py monitor
  
  # List zones
  ./lutron_cli.py list
"""
    )
    parser.add_argument('--ip', '-i', default=DEFAULT_BRIDGE_IP,
                        help=f'IP address of the Lutron bridge (default: {DEFAULT_BRIDGE_IP})')
    
    # Create subparsers for different command groups
    subparsers = parser.add_subparsers(dest='command', help='Command group')
    subparsers.required = True
    
    # ZONE command - control a specific zone
    zone_parser = subparsers.add_parser('zone', help='Control a specific light zone')
    zone_parser.add_argument('--zone-id', '-z', type=int, required=True,
                            help='Zone ID to control')
    
    zone_subparsers = zone_parser.add_subparsers(dest='action', help='Zone action')
    zone_subparsers.required = True
    
    # Zone actions
    zone_subparsers.add_parser('on', help='Turn zone ON')
    zone_subparsers.add_parser('off', help='Turn zone OFF')
    
    zone_set_parser = zone_subparsers.add_parser('set', help='Set zone to specific level')
    zone_set_parser.add_argument('--level', '-l', type=float, required=True,
                               help='Brightness level (0.0-100.0)')
    
    # ROOM command - control a specific room
    room_parser = subparsers.add_parser('room', help='Control all lights in a room')
    room_parser.add_argument('room_name', choices=['kitchen', 'bedroom'],
                           help='Room name to control')
    room_parser.add_argument('--mode', '-m', choices=['sequential', 'batch'], default='batch',
                          help='Control mode: sequential or batch (default: batch)')
    room_parser.add_argument('--delay', '-d', type=float, default=0.5,
                          help='Delay between lights in sequential mode (default: 0.5s)')
    
    room_subparsers = room_parser.add_subparsers(dest='action', help='Room action')
    room_subparsers.required = True
    
    # Room actions
    room_subparsers.add_parser('on', help='Turn all room lights ON')
    room_subparsers.add_parser('off', help='Turn all room lights OFF')
    
    room_set_parser = room_subparsers.add_parser('set', help='Set all room lights to specific level')
    room_set_parser.add_argument('--level', '-l', type=float, required=True,
                               help='Brightness level (0.0-100.0)')
    
    # SHOW command - run a light show
    show_parser = subparsers.add_parser('show', help='Run a light show sequence')
    show_parser.add_argument('show_name', choices=['kitchen-standard', 'kitchen-optimized'],
                           help='Light show name to run')
    
    # PARTY command - run the randomized party lights
    party_parser = subparsers.add_parser('party', help='Run the kitchen party lights (random patterns)')
    party_parser.add_argument('--min-interval', type=float, default=0.2,
                            help='Minimum interval between changes (default: 0.2 seconds)')
    party_parser.add_argument('--max-interval', type=float, default=2.0,
                            help='Maximum interval between changes (default: 2.0 seconds)')
    party_parser.add_argument('--pattern-duration', type=float, default=10.0,
                            help='How long to run each pattern (default: 10.0 seconds)')
    
    # MONITOR command - monitor bridge activity
    monitor_parser = subparsers.add_parser('monitor', help='Monitor Lutron bridge activity')
    monitor_parser.add_argument('--timeout', '-t', type=int, default=60,
                              help='Connection timeout in seconds (default: 60)')
    
    # LIST command - list available zones
    list_parser = subparsers.add_parser('list', help='List available zones')
    list_parser.add_argument('--area', '-a', help='Filter zones by area name')
    
    return parser.parse_args()

def control_zone(args):
    """Control a single zone"""
    with LutronController(args.ip) as controller:
        if not controller.connected:
            print(f"Failed to connect to bridge at {args.ip}")
            return 1
            
        if args.action == 'on':
            print(f"Turning zone {args.zone_id} ON")
            controller.set_light(args.zone_id, 100.0)
        elif args.action == 'off':
            print(f"Turning zone {args.zone_id} OFF")
            controller.set_light(args.zone_id, 0.0)
        elif args.action == 'set':
            level = max(0.0, min(100.0, args.level))
            print(f"Setting zone {args.zone_id} to {level}%")
            controller.set_light(args.zone_id, level)
    
    return 0

def control_room(args):
    """Control all lights in a room"""
    # Select room
    if args.room_name == 'kitchen':
        room_zones = KITCHEN_ALL
        room_display = "Kitchen"
    elif args.room_name == 'bedroom':
        room_zones = [MASTER_BEDROOM["BAY_WINDOW"]]
        room_display = "Master Bedroom"
    else:
        print(f"Unknown room: {args.room_name}")
        return 1
    
    # Display zones
    print(f"\nControlling {room_display} Lights")
    print("-" * (len(room_display) + 18))
    print_zones(room_zones)
    
    # Connect and control
    with LutronController(args.ip) as controller:
        if not controller.connected:
            print(f"Failed to connect to bridge at {args.ip}")
            return 1
        
        # Determine level
        level = 0.0
        if args.action == 'on':
            level = 100.0
            print(f"Turning {room_display} lights ON")
        elif args.action == 'off':
            level = 0.0
            print(f"Turning {room_display} lights OFF")
        elif args.action == 'set':
            level = max(0.0, min(100.0, args.level))
            print(f"Setting {room_display} lights to {level}%")
        
        # Control the lights
        if args.mode == 'sequential':
            controller.set_lights_sequential(room_zones, level, args.delay)
        else:  # batch mode
            controller.set_lights_batch(room_zones, level)
    
    return 0

def monitor_bridge(args):
    """Monitor bridge activity (imported from lutron_monitor.py)"""
    from scripts.lutron_monitor import main as monitor_main
    # Create sys.argv for the monitor module
    sys.argv = [sys.argv[0]]
    if args.ip != DEFAULT_BRIDGE_IP:
        sys.argv.extend(['--ip', args.ip])
    if args.timeout != 60:
        sys.argv.extend(['--timeout', str(args.timeout)])
    
    return monitor_main()

def list_zones(args):
    """List available zones"""
    all_zones = []
    
    # Add kitchen zones
    all_zones.extend(KITCHEN_ALL)
    
    # Add bedroom zones
    all_zones.append(MASTER_BEDROOM["BAY_WINDOW"])
    
    # Filter by area if specified
    if args.area:
        area_lower = args.area.lower()
        filtered_zones = []
        for zone in all_zones:
            # Check area in name
            if 'kitchen' in area_lower and 'kitchen' in zone.area.lower():
                filtered_zones.append(zone)
            elif 'bedroom' in area_lower and 'bedroom' in zone.area.lower():
                filtered_zones.append(zone)
            # Also check name directly
            elif area_lower in zone.name.lower():
                filtered_zones.append(zone)
        all_zones = filtered_zones
    
    # Print zones
    if all_zones:
        print("\nAvailable Zones:")
        print("-" * 16)
        for zone in sorted(all_zones, key=lambda z: z.id):
            print(f"  Zone {zone.id:>2}: {zone.name} ({zone.area})")
    else:
        if args.area:
            print(f"No zones found matching '{args.area}'")
        else:
            print("No zones available")
    
    return 0

def run_show(args):
    """Run a light show sequence"""
    if args.show_name == 'kitchen-standard':
        from scripts.kitchen_show import run_light_show
    elif args.show_name == 'kitchen-optimized':
        from scripts.kitchen_show_optimized import run_light_show
    else:
        print(f"Unknown show: {args.show_name}")
        return 1
    
    # Create controller and run show
    with LutronController(args.ip) as controller:
        if not controller.connected:
            print(f"Failed to connect to bridge at {args.ip}")
            return 1
        
        try:
            run_light_show(controller)
            return 0
        except KeyboardInterrupt:
            print("\n\nLight show interrupted! Turning lights off...")
            controller.set_lights_batch(KITCHEN_ALL, 0.0)
            return 1

def run_party(args):
    """Run the kitchen party lights"""
    from scripts.kitchen_party import run_party_lights
    
    # Create controller and run party
    with LutronController(args.ip) as controller:
        if not controller.connected:
            print(f"Failed to connect to bridge at {args.ip}")
            return 1
        
        try:
            run_party_lights(
                controller,
                min_interval=args.min_interval,
                max_interval=args.max_interval,
                pattern_duration=args.pattern_duration
            )
            return 0
        except KeyboardInterrupt:
            print("\n\nParty interrupted! Turning lights off...")
            controller.set_lights_batch(KITCHEN_ALL, 0.0)
            return 1

def main():
    """Main entry point for the unified CLI"""
    args = parse_args()
    
    # Route to appropriate handler based on command
    if args.command == 'zone':
        return control_zone(args)
    elif args.command == 'room':
        return control_room(args)
    elif args.command == 'show':
        return run_show(args)
    elif args.command == 'party':
        return run_party(args)
    elif args.command == 'monitor':
        return monitor_bridge(args)
    elif args.command == 'list':
        return list_zones(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 