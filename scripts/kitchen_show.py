#!/usr/bin/env python3
"""
Kitchen Light Show - Fun lighting sequence for kitchen lights
"""
import argparse
import sys
import time
import os
import sys

# Add parent directory to path to allow imports when run directly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from src.lutron_controller import LutronController
from src.lutron_zones import KITCHEN_ALL, print_zones

# Hardcoded bridge IP address
DEFAULT_BRIDGE_IP = "192.168.49.91"

def run_light_show(controller):
    """
    Run the kitchen light show sequence
    
    Args:
        controller: LutronController instance (already connected)
    """
    print("\n🎭 Starting Kitchen Light Show! 🎭\n")
    
    # Part 1: Quick on/off sequence at start
    print("🌑 Initial on/off sequence")
    # Turn all off
    controller.set_lights_batch(KITCHEN_ALL, 0.0)
    time.sleep(1)  # Short pause
    
    # Turn all on
    print("💡 All lights ON")
    controller.set_lights_batch(KITCHEN_ALL, 100.0)
    time.sleep(1)  # Short pause
    
    # Turn all off
    print("🔅 All lights OFF")
    controller.set_lights_batch(KITCHEN_ALL, 0.0)
    time.sleep(1)  # Short pause
    
    # Part 2: Turning lights on sequentially
    print("\n🌓 Turning each light ON sequentially")
    controller.set_lights_sequential(KITCHEN_ALL, 25.0, delay=1.0)
    time.sleep(2)  # Short pause between sequences
    
    # Part 3: Increasing brightness sequentially
    print("\n🌕 Increasing each light sequentially")
    controller.set_lights_sequential(KITCHEN_ALL, 50.0, delay=1.0)
    controller.set_lights_sequential(KITCHEN_ALL, 75.0, delay=1.0)
    controller.set_lights_sequential(KITCHEN_ALL, 100.0, delay=1.0)
    
    # Part 4: Wait with all lights at full brightness
    print("\n⏱️  All lights at full brightness for 10 seconds")
    time.sleep(10)
    
    # Part 5: Cascade dimming effect
    print("\n🔅 Starting cascade dimming effect")
    
    # Start with all lights at 100%
    current_levels = {zone.id: 100.0 for zone in KITCHEN_ALL}
    all_off = False
    
    # Keep dimming until all lights are off
    while not all_off:
        all_off = True  # Assume all will be off after this iteration
        
        # Go through each light
        for zone in KITCHEN_ALL:
            zone_id = zone.id
            name = zone.name
            current_level = current_levels[zone_id]
            
            # If this light isn't off yet, dim it by 2%
            if current_level > 0:
                all_off = False  # At least one light is still on
                new_level = max(0, current_level - 2.0)
                current_levels[zone_id] = new_level
                
                # Only print messages for full percentages to reduce noise
                if int(new_level) % 10 == 0:
                    print(f"  - {name} at {new_level:.0f}%")
                
                # Set the light to the new level
                controller.set_light(zone_id, new_level)
                
                # Add a small delay between lights to avoid overwhelming the bridge
                time.sleep(0.05)  # 50ms delay between controlling different lights
        
        # Tiny delay between iterations to make the effect visible
        time.sleep(0.1)
    
    print("\n🎬 Light show complete! All lights are off.")

def parse_args():
    parser = argparse.ArgumentParser(description='Run a fun light show in the kitchen')
    parser.add_argument('--ip', '-i', default=DEFAULT_BRIDGE_IP, 
                        help=f'IP address of the Lutron bridge (default: {DEFAULT_BRIDGE_IP})')
    return parser.parse_args()

def main():
    args = parse_args()
    
    print("\nKitchen Light Show")
    print("-----------------")
    print_zones(KITCHEN_ALL, "Lights in this show:")
    
    # Create controller and connect
    with LutronController(args.ip) as controller:
        if not controller.connected:
            print("Failed to connect to the bridge")
            return 1
        
        try:
            # Run the light show
            run_light_show(controller)
            return 0
        except KeyboardInterrupt:
            print("\n\nLight show interrupted! Turning all lights off...")
            controller.set_lights_batch(KITCHEN_ALL, 0.0)
            print("All lights turned off.")
            return 1

if __name__ == "__main__":
    sys.exit(main()) 