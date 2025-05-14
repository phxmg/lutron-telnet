#!/usr/bin/env python3
"""
Lutron Zones - Definitions of light zones by area
"""

# Master Bedroom lights
MASTER_BEDROOM = {
    "BAY_WINDOW": {"id": 10, "name": "Bay Window Lights"}
}

# Kitchen lights
KITCHEN = {
    "SINK": {"id": 27, "name": "Sink Light"},
    "PENDANTS": {"id": 30, "name": "Island Pendants"},
    "ISLAND": {"id": 31, "name": "Island Lights"},
    "MAIN": {"id": 33, "name": "Main Lights"}
}

# All Kitchen lights as a list
KITCHEN_ALL = [
    KITCHEN["SINK"],
    KITCHEN["PENDANTS"],
    KITCHEN["ISLAND"],
    KITCHEN["MAIN"]
]

def get_zone_names(zones):
    """Get a formatted list of zone names for display"""
    return [f"{zone['name']} (Zone {zone['id']})" for zone in zones]

def print_zones(zones, title=None):
    """Print a list of zones in a formatted way"""
    if title:
        print(f"\n{title}\n")
        print("-" * (len(title) + 2))
    
    for zone in zones:
        print(f"  Zone {zone['id']:>2}: {zone['name']}")
    
    print("") 