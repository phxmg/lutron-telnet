#!/usr/bin/env python3
"""
Lutron Zones - Definitions of light zones by area with metadata
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Zone:
    """Zone definition with metadata"""
    id: int
    name: str
    area: str = ""
    type: str = "Light"
    
    def to_dict(self):
        """Convert to dictionary for backward compatibility"""
        return {
            "id": self.id,
            "name": self.name,
            "area": self.area,
            "type": self.type
        }

# Master Bedroom zones
MASTER_BEDROOM_AREA = "Master Bedroom"
MASTER_BEDROOM = {
    "BAY_WINDOW": Zone(id=10, name="Bay Window Lights", area=MASTER_BEDROOM_AREA)
}

# Kitchen zones
KITCHEN_AREA = "Kitchen"
KITCHEN = {
    "SINK": Zone(id=27, name="Sink Light", area=KITCHEN_AREA),
    "PENDANTS": Zone(id=30, name="Island Pendants", area=KITCHEN_AREA),
    "ISLAND": Zone(id=31, name="Island Lights", area=KITCHEN_AREA),
    "MAIN": Zone(id=33, name="Main Lights", area=KITCHEN_AREA)
}

# All Kitchen lights as a list
KITCHEN_ALL = [
    KITCHEN["SINK"],
    KITCHEN["PENDANTS"],
    KITCHEN["ISLAND"],
    KITCHEN["MAIN"]
]

# All zones in a flat list (for searching)
ALL_ZONES = [
    *KITCHEN_ALL,
    MASTER_BEDROOM["BAY_WINDOW"]
]

def find_zone_by_id(zone_id: int) -> Optional[Zone]:
    """Find a zone by its ID"""
    for zone in ALL_ZONES:
        if zone.id == zone_id:
            return zone
    return None

def find_zones_by_area(area_name: str) -> List[Zone]:
    """Find all zones in a specific area"""
    area_lower = area_name.lower()
    return [zone for zone in ALL_ZONES 
            if area_lower in zone.area.lower()]

def get_zone_names(zones: List[Zone]) -> List[str]:
    """Get a formatted list of zone names for display"""
    return [f"{zone.name} (Zone {zone.id})" for zone in zones]

def print_zones(zones: List[Zone], title: Optional[str] = None) -> None:
    """Print a list of zones in a formatted way"""
    if title:
        print(f"\n{title}\n")
        print("-" * (len(title) + 2))
    
    for zone in zones:
        print(f"  Zone {zone.id:>2}: {zone.name}")
    
    print("") 