#!/usr/bin/env python3

import sys
import time
import argparse
from lutron_telnet import LutronTelnet

def control_device(bridge_ip, command, zone_id=None, level=None):
    """Control a Lutron device via Telnet."""
    # Initialize connection
    lutron = LutronTelnet(bridge_ip)
    
    try:
        # Connect to the bridge
        print(f"Connecting to bridge at {bridge_ip}...")
        if not lutron.connect():
            print("Failed to connect to bridge!")
            return False
        
        # Execute the command
        if command == "list":
            # List all devices and zones
            zones = lutron.get_zones()
            areas = lutron.get_areas()
            devices = lutron.get_devices()
            
            print("\n--- LUTRON TELNET STATUS ---")
            
            # Print areas
            if areas:
                print("\nAreas:")
                for area_id, area in areas.items():
                    print(f"  Area {area_id}: {area.get('name')}")
            else:
                print("\nNo areas found.")
            
            # Print zones
            if zones:
                print("\nZones (Controllable Entities):")
                for zone_id, zone in zones.items():
                    print(f"  Zone {zone_id}: {zone.get('name')} (Area: {zone.get('area_name', 'Unknown')})")
            else:
                print("\nNo zones found.")
            
            # Print devices
            if devices:
                print("\nDevices:")
                for device_id, device in devices.items():
                    print(f"  Device {device_id}: {device.get('name')} (Type: {device.get('type', 'Unknown')})")
            else:
                print("\nNo devices found.")
                
        elif command == "on" and zone_id:
            # Turn on a zone (set to 100%)
            print(f"Turning zone {zone_id} ON (100%)...")
            success = lutron.set_zone_level(zone_id, 100.0)
            if success:
                print(f"Successfully turned zone {zone_id} ON")
            else:
                print(f"Failed to turn zone {zone_id} ON")
                
        elif command == "off" and zone_id:
            # Turn off a zone (set to 0%)
            print(f"Turning zone {zone_id} OFF (0%)...")
            success = lutron.set_zone_level(zone_id, 0.0)
            if success:
                print(f"Successfully turned zone {zone_id} OFF")
            else:
                print(f"Failed to turn zone {zone_id} OFF")
                
        elif command == "set" and zone_id and level is not None:
            # Set a zone to specific level
            print(f"Setting zone {zone_id} to level {level}%...")
            success = lutron.set_zone_level(zone_id, level)
            if success:
                print(f"Successfully set zone {zone_id} to level {level}%")
            else:
                print(f"Failed to set zone {zone_id} to level {level}%")
                
        elif command == "monitor":
            # Monitor for events
            def event_callback(line):
                print(f"EVENT: {line}")
            
            # Add our callback and start monitoring
            lutron.add_callback(event_callback)
            lutron.start_monitoring()
            
            print("\nMonitoring for events. Press Ctrl+C to stop...")
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nStopping monitoring...")
            
            # Clean up
            lutron.remove_callback(event_callback)
            lutron.stop_monitoring()
            
        else:
            print(f"Invalid command: {command}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Close the connection
        lutron.close()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Control Lutron devices via Telnet')
    parser.add_argument('bridge_ip', help='IP address of the Lutron bridge')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all zones and devices')
    
    # On command
    on_parser = subparsers.add_parser('on', help='Turn a zone ON')
    on_parser.add_argument('zone_id', help='Zone ID to turn on')
    
    # Off command
    off_parser = subparsers.add_parser('off', help='Turn a zone OFF')
    off_parser.add_argument('zone_id', help='Zone ID to turn off')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set a zone to specific level')
    set_parser.add_argument('zone_id', help='Zone ID to set')
    set_parser.add_argument('level', type=float, help='Level to set (0-100)')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor events from the bridge')
    
    args = parser.parse_args()
    
    # Get parameters
    bridge_ip = args.bridge_ip
    command = args.command
    zone_id = getattr(args, 'zone_id', None)
    level = getattr(args, 'level', None)
    
    # Execute command
    if not command:
        parser.print_help()
        return
        
    success = control_device(bridge_ip, command, zone_id, level)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 