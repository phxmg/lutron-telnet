#!/usr/bin/env python3
import argparse
import json
import sys

def parse_args():
    parser = argparse.ArgumentParser(description='List zones from Lutron integration report')
    parser.add_argument('--report', '-r', required=True, help='Path to integration report JSON file')
    return parser.parse_args()

def main():
    args = parse_args()
    
    try:
        # Load the integration report
        with open(args.report, 'r') as f:
            report = json.load(f)
        
        # Extract areas and zones
        areas = {area['href']: area['Name'] for area in report.get('Areas', [])}
        zones = report.get('Zones', [])
        
        # Organize zones by areas
        zones_by_area = {}
        
        for zone in zones:
            area_href = zone.get('Area', {}).get('href')
            if area_href:
                area_name = areas.get(area_href, 'Unknown Area')
                if area_name not in zones_by_area:
                    zones_by_area[area_name] = []
                
                zones_by_area[area_name].append({
                    'id': zone.get('ID', 'Unknown'),
                    'name': zone.get('Name', 'Unknown'),
                })
        
        # Print zones by area
        print("\nLutron Caseta Zones by Area:\n")
        
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