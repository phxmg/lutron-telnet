#!/usr/bin/env python3
"""
Kitchen Party Lights - Randomized light show that runs until interrupted
"""
import argparse
import sys
import time
import random
import os
import signal

# Add parent directory to path to allow imports when run directly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from src.lutron_controller import LutronController
from src.lutron_zones import KITCHEN_ALL, print_zones

# Hardcoded bridge IP address
DEFAULT_BRIDGE_IP = "192.168.49.91"

# Color ANSI escape codes for fun terminal output
COLORS = [
    '\033[91m',  # Red
    '\033[92m',  # Green
    '\033[93m',  # Yellow
    '\033[94m',  # Blue
    '\033[95m',  # Magenta
    '\033[96m',  # Cyan
]
RESET = '\033[0m'  # Reset color

# Fun emoji patterns
EMOJIS = [
    "✨", "🎉", "🔥", "🌟", "💫", "⚡", "🎵", "🎊", "🎭", "🥳", "🚀", "💥", "🎇", "🎆"
]

# Patterns for the light show
PATTERNS = [
    "flash_all",         # Flash all lights together
    "chase",             # Chase pattern one light at a time
    "random_individual", # Random individual lights
    "wave",              # Wave pattern from left to right
    "pulse",             # Pulse all lights up and down
    "strobe",            # Quick strobe effect
    "alternate",         # Alternate between different lights
    "random_levels",     # Set random brightness levels
]

def random_color():
    """Return a random terminal color code"""
    return random.choice(COLORS)

def random_emoji():
    """Return a random fun emoji"""
    return random.choice(EMOJIS)

def print_party(message):
    """Print a colorful party message"""
    color = random_color()
    emoji = random_emoji()
    print(f"{color}{emoji} {message} {emoji}{RESET}")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run a randomized party light show in the kitchen')
    parser.add_argument('--ip', '-i', default=DEFAULT_BRIDGE_IP, 
                        help=f'IP address of the Lutron bridge (default: {DEFAULT_BRIDGE_IP})')
    parser.add_argument('--min-interval', type=float, default=0.2,
                        help='Minimum interval between changes (default: 0.2 seconds)')
    parser.add_argument('--max-interval', type=float, default=2.0,
                        help='Maximum interval between changes (default: 2.0 seconds)')
    parser.add_argument('--pattern-duration', type=float, default=10.0,
                        help='How long to run each pattern before switching (default: 10.0 seconds)')
    return parser.parse_args()

def flash_all(controller, zones, duration, min_interval, max_interval):
    """Flash all lights on and off"""
    print_party("FLASH ALL LIGHTS")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Choose a random level (on, off, or dim)
        level = random.choice([0, 50, 100])
        
        # Flash all lights together
        controller.set_lights_batch(zones, level)
        
        # Wait a random interval
        interval = random.uniform(min_interval, max_interval)
        time.sleep(interval)

def chase(controller, zones, duration, min_interval, max_interval):
    """Chase pattern - one light at a time"""
    print_party("CHASE PATTERN")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Turn all lights off
        controller.set_lights_batch(zones, 0)
        
        # Turn on one light at a time
        for zone in zones:
            # Random level for the active light
            level = random.choice([50, 100])
            controller.set_light(zone, level)
            
            # Random interval
            interval = random.uniform(min_interval, max_interval)
            time.sleep(interval)
            
            # Turn off before moving to next
            controller.set_light(zone, 0)

def random_individual(controller, zones, duration, min_interval, max_interval):
    """Random individual lights"""
    print_party("RANDOM INDIVIDUAL LIGHTS")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Select a random zone
        zone = random.choice(zones)
        
        # Choose a random level
        level = random.choice([0, 50, 100])
        
        # Set the light
        controller.set_light(zone, level)
        
        # Wait a random interval
        interval = random.uniform(min_interval, max_interval)
        time.sleep(interval)

def wave(controller, zones, duration, min_interval, max_interval):
    """Wave pattern from left to right"""
    print_party("WAVE PATTERN")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Choose a level for this wave
        level = random.choice([50, 100])
        
        # Wave forward
        for zone in zones:
            controller.set_light(zone, level)
            time.sleep(min_interval)
        
        # Wait a little
        time.sleep(max_interval)
        
        # Wave backward (turn off)
        for zone in reversed(zones):
            controller.set_light(zone, 0)
            time.sleep(min_interval)
        
        # Wait a little
        time.sleep(max_interval)

def pulse(controller, zones, duration, min_interval, max_interval):
    """Pulse all lights up and down"""
    print_party("PULSE EFFECT")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Pulse up
        for level in range(0, 101, 10):
            controller.set_lights_batch(zones, level)
            time.sleep(min_interval)
        
        # Pulse down
        for level in range(100, -1, -10):
            controller.set_lights_batch(zones, level)
            time.sleep(min_interval)
        
        # Random pause between pulses
        time.sleep(random.uniform(min_interval, max_interval))

def strobe(controller, zones, duration, min_interval, max_interval):
    """Quick strobe effect"""
    print_party("STROBE EFFECT")
    end_time = time.time() + duration
    
    # Use shortest interval for strobe
    strobe_interval = min_interval / 2
    
    while time.time() < end_time:
        # Strobe on
        controller.set_lights_batch(zones, 100)
        time.sleep(strobe_interval)
        
        # Strobe off
        controller.set_lights_batch(zones, 0)
        time.sleep(strobe_interval)
        
        # Every few strobe cycles, pause briefly
        if random.random() < 0.2:  # 20% chance
            time.sleep(max_interval)

def alternate(controller, zones, duration, min_interval, max_interval):
    """Alternate between different lights"""
    print_party("ALTERNATING PATTERN")
    end_time = time.time() + duration
    
    # Split into two groups
    group_a = zones[::2]  # Even indices
    group_b = zones[1::2]  # Odd indices
    
    while time.time() < end_time:
        # Group A on, Group B off
        for zone in group_a:
            controller.set_light(zone, 100)
        for zone in group_b:
            controller.set_light(zone, 0)
        
        time.sleep(random.uniform(min_interval, max_interval))
        
        # Group A off, Group B on
        for zone in group_a:
            controller.set_light(zone, 0)
        for zone in group_b:
            controller.set_light(zone, 100)
        
        time.sleep(random.uniform(min_interval, max_interval))

def random_levels(controller, zones, duration, min_interval, max_interval):
    """Set random brightness levels"""
    print_party("RANDOM BRIGHTNESS LEVELS")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Set each light to a random level
        for zone in zones:
            level = random.randint(0, 100)
            controller.set_light(zone, level)
        
        # Wait a random interval
        interval = random.uniform(min_interval, max_interval)
        time.sleep(interval)

def run_party_lights(controller, min_interval=0.2, max_interval=2.0, pattern_duration=10.0):
    """
    Run the randomized party light show
    
    Args:
        controller: LutronController instance (already connected)
        min_interval: Minimum interval between changes (seconds)
        max_interval: Maximum interval between changes (seconds)
        pattern_duration: How long to run each pattern before switching (seconds)
    """
    print("\n🎵 Starting Kitchen Party Lights! 🎵\n")
    print("Press Ctrl+C to stop the party\n")
    
    # Pattern functions map
    patterns = {
        "flash_all": flash_all,
        "chase": chase,
        "random_individual": random_individual,
        "wave": wave, 
        "pulse": pulse,
        "strobe": strobe,
        "alternate": alternate,
        "random_levels": random_levels
    }
    
    try:
        while True:
            # Select a random pattern
            pattern_name = random.choice(PATTERNS)
            pattern_func = patterns[pattern_name]
            
            # Run the pattern
            pattern_func(controller, KITCHEN_ALL, pattern_duration, min_interval, max_interval)
    
    except KeyboardInterrupt:
        print("\n\n🎉 Party's over! Turning all lights off... 🎉")
        controller.set_lights_batch(KITCHEN_ALL, 0.0)
        print("All lights turned off.")

def main():
    """Main entry point"""
    args = parse_args()
    
    # Print banner
    print("\n" + "=" * 40)
    print("🎵 🎶  KITCHEN PARTY LIGHTS  🎶 🎵")
    print("=" * 40)
    print_zones(KITCHEN_ALL, "Lights in this party:")
    
    # Create controller and connect
    with LutronController(args.ip) as controller:
        if not controller.connected:
            print("Failed to connect to the bridge")
            return 1
        
        try:
            # Run the party lights show
            run_party_lights(
                controller, 
                min_interval=args.min_interval,
                max_interval=args.max_interval,
                pattern_duration=args.pattern_duration
            )
            return 0
        except KeyboardInterrupt:
            print("\n\nParty interrupted! Turning all lights off...")
            controller.set_lights_batch(KITCHEN_ALL, 0.0)
            print("All lights turned off.")
            return 1

if __name__ == "__main__":
    sys.exit(main()) 