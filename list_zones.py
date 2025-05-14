#!/usr/bin/env python3
import argparse
import json
import sys

# Hardcoded bridge IP address
DEFAULT_BRIDGE_IP = "192.168.49.91"

def parse_args():
    parser = argparse.ArgumentParser(description='List zones from Lutron integration report')
    parser.add_argument('--report', '-r', required=True, help='Path to integration report JSON file')
    parser.add_argument('--area', '-a', help='Filter zones by area name (case-insensitive)')
    parser.add_argument('--ip', '-i', default=DEFAULT_BRIDGE_IP,
                        help=f'IP address of the Lutron bridge (default: {DEFAULT_BRIDGE_IP})')
    return parser.parse_args()

def main():
    args = parse_args()
    
    try:
        # Load the integration report
        with open(args.report, 'r') as f:
            report = json.load(f)
        
        # Extract zones
        zones = report.get('LIPIdList', {}).get('Zones', [])
        
        # Organize zones by areas
        zones_by_area = {}
        
        for zone in zones:
            area_name = zone.get('Area', {}).get('Name', 'Unknown Area')
            if area_name not in zones_by_area:
                zones_by_area[area_name] = []
            
            zones_by_area[area_name].append({
                'id': zone.get('ID', 'Unknown'),
                'name': zone.get('Name', 'Unknown'),
            })
        
        # Filter by area if specified
        if args.area:
            filtered_areas = {}
            for area_name, zone_list in zones_by_area.items():
                if args.area.lower() in area_name.lower():
                    filtered_areas[area_name] = zone_list
            zones_by_area = filtered_areas
        
        # Print zones by area
        if not zones_by_area:
            if args.area:
                print(f"No zones found for area matching '{args.area}'")
            else:
                print("No zones found in the integration report")
            return 1
        
        print("\nLutron Caseta Zones by Area:\n")
        print(f"Bridge IP: {args.ip}\n")
        
        for area_name, zone_list in sorted(zones_by_area.items()):
            print(f"Area: {area_name}")
            print("-" * (len(area_name) + 6))
            
            for zone in sorted(zone_list, key=lambda z: z['id']):
                print(f"  Zone {zone['id']:>2}: {zone['name']}")
            
            print()
        
        return 0
        
    except FileNotFoundError:
        print(f"Error: Report file '{args.report}' not found.")
        return 1
    except json.JSONDecodeError:
        print(f"Error: Report file '{args.report}' is not valid JSON.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 