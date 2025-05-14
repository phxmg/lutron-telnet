#!/usr/bin/env python3
"""
Lutron Controller - High-level control functions for Lutron lights
"""

import threading
import time
from src.lutron_quick import LutronQuick

class LutronController:
    """Advanced controller with batch and sequential operations for Lutron lights"""
    
    def __init__(self, host, port=23, timeout=3):
        """Initialize the controller with connection parameters"""
        self.quick = LutronQuick(host, port, timeout)
        self.connected = False
    
    def connect(self):
        """Connect to the Lutron bridge"""
        self.connected = self.quick.connect()
        return self.connected
    
    def close(self):
        """Close the connection"""
        if self.connected:
            self.quick.close()
            self.connected = False
    
    def set_light(self, zone_id, level):
        """Control a single light zone"""
        if not self.connected:
            raise RuntimeError("Not connected to bridge")
            
        return self.quick.set_light(zone_id, level)
    
    def _set_light_thread(self, zone_id, level):
        """Helper function for threading - controls a single light"""
        self.quick.set_light(zone_id, level)
    
    def set_lights_sequential(self, zones, level, delay=0.5, verbose=True):
        """
        Control multiple lights sequentially
        
        Args:
            zones: List of zones. Each zone can be either:
                - An integer (zone_id)
                - A dict with 'id' and 'name' keys
            level: Brightness level (0-100)
            delay: Delay between commands in seconds
            verbose: Whether to print status messages
        """
        if not self.connected:
            raise RuntimeError("Not connected to bridge")
            
        level = max(0.0, min(100.0, level))
        
        if verbose:
            print(f"Setting {len(zones)} lights to {level}% (sequential mode, {delay}s delay)")
        
        # Process each zone
        for zone in zones:
            # Handle both integer zone_ids and dict with id/name
            if isinstance(zone, dict):
                zone_id = zone['id']
                zone_name = zone.get('name', f"Zone {zone_id}")
                if verbose:
                    print(f"  - Setting {zone_name} (Zone {zone_id}) to {level}%")
            else:
                zone_id = zone
                if verbose:
                    print(f"  - Setting Zone {zone_id} to {level}%")
            
            # Control this light
            self.quick.set_light(zone_id, level)
            
            # Wait before next command
            time.sleep(delay)
    
    def set_lights_batch(self, zones, level, verbose=True):
        """
        Control multiple lights simultaneously using threads
        
        Args:
            zones: List of zones. Each zone can be either:
                - An integer (zone_id)
                - A dict with 'id' and 'name' keys
            level: Brightness level (0-100)
            verbose: Whether to print status messages
        """
        if not self.connected:
            raise RuntimeError("Not connected to bridge")
            
        level = max(0.0, min(100.0, level))
        
        if verbose:
            print(f"Setting {len(zones)} lights to {level}% (batch mode)")
        
        # Create a thread for each light
        threads = []
        
        for zone in zones:
            # Handle both integer zone_ids and dict with id/name
            if isinstance(zone, dict):
                zone_id = zone['id']
                zone_name = zone.get('name', f"Zone {zone_id}")
                if verbose:
                    print(f"  - Queuing {zone_name} (Zone {zone_id})")
            else:
                zone_id = zone
                if verbose:
                    print(f"  - Queuing Zone {zone_id}")
            
            # Create thread for this light
            thread = threading.Thread(
                target=self._set_light_thread,
                args=(zone_id, level)
            )
            threads.append(thread)
        
        # Start all threads with a small stagger
        for thread in threads:
            thread.start()
            time.sleep(0.1)  # Small stagger to avoid flooding the bridge
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
    def __enter__(self):
        """Support for with statement"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for with statement"""
        self.close() 