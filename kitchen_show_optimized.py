#!/usr/bin/env python3
"""
Kitchen Light Show (Optimized) - Fun lighting sequence with reduced command count
"""
import argparse
import sys
import time
from src.lutron_controller import LutronController
from src.lutron_zones import KITCHEN_ALL, print_zones

# Hardcoded bridge IP address
DEFAULT_BRIDGE_IP = "192.168.49.91"

def parse_args():
    parser = argparse.ArgumentParser(description='Run an optimized light show in the kitchen')
    parser.add_argument('--ip', '-i', default=DEFAULT_BRIDGE_IP, 
                        help=f'IP address of the Lutron bridge (default: {DEFAULT_BRIDGE_IP})')
    return parser.parse_args()

def run_light_show(controller):
    """Run the kitchen light show sequence with optimized command count"""
    print("\n🎭 Starting Kitchen Light Show (Optimized)! 🎭\n")
    
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
    
    # Part 2: Turn lights on sequentially in steps
    print("\n🌓 Turning lights ON sequentially in steps")
    
    # Sequential steps from 0% to 100%
    for percentage in [25, 50, 75, 100]:
        print(f"\n  Setting all lights to {percentage}%")
        for zone in KITCHEN_ALL:
            zone_id = zone['id']
            name = zone['name']
            print(f"    - Setting {name} (Zone {zone_id}) to {percentage}%")
            controller.set_light(zone_id, percentage)
            time.sleep(1.0)  # 1 second between lights
    
    # Part 3: Wait with all lights at full brightness
    print("\n⏱️  All lights at full brightness for 10 seconds")
    time.sleep(10)
    
    # Part 4: Optimized cascade dimming with modified delays
    print("\n🔅 Starting optimized cascade dimming effect")
    
    # Increasing 10% at a time from 0% to 100%
    current_levels = {zone['id']: 0.0 for zone in KITCHEN_ALL}  # Start at 0%
    
    # Go from 0% → 10% → 20% → ... → 90% → 100%
    for level in range(10, 110, 10):  # 10, 20, 30, ... 100
        print(f"\n  Increasing to {level}%")
        for zone in KITCHEN_ALL:
            zone_id = zone['id']
            name = zone['name']
            print(f"    - Setting {name} to {level}%")
            controller.set_light(zone_id, level)
            time.sleep(0.25)  # 250ms between lights at each step (up from 50ms)
        
        # Pause between iterations
        time.sleep(0.25)  # 250ms pause after each complete iteration (up from 100ms)
    
    # Part 5: Decreasing 10% at a time from 100% to 0%
    for level in range(90, -1, -10):  # 90, 80, 70, ... 10, 0
        print(f"\n  Dimming to {level}%")
        for zone in KITCHEN_ALL:
            zone_id = zone['id']
            name = zone['name']
            print(f"    - Setting {name} to {level}%")
            controller.set_light(zone_id, level)
            time.sleep(0.25)  # 250ms between lights at each step
        
        # Pause between iterations
        time.sleep(0.25)  # 250ms pause after each complete iteration
    
    print("\n🎬 Light show complete! All lights are off.")

def main():
    args = parse_args()
    
    print("\nKitchen Light Show (Optimized)")
    print("-----------------------------")
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