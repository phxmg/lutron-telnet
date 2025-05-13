#!/usr/bin/env python3

import socket
import time
import sys
import json
import argparse
import threading
from typing import Dict, List, Optional, Any

class LutronBridge:
    """Simple interface to control Lutron Caseta devices via Telnet."""
    
    def __init__(self, host: str, port: int = 23, username: str = "lutron", password: str = "integration"):
        """Initialize the connection to the Lutron bridge.
        
        Args:
            host: IP address of the bridge
            port: Telnet port (default: 23)
            username: Username for authentication (default: "lutron")
            password: Password for authentication (default: "integration")
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socket = None
        self.buffer = b""
        self.connected = False
        self.lock = threading.Lock()
        
        # Load integration report data
        self.zones = {}
        self.devices = {}
        self.areas = {}
        
    def connect(self) -> bool:
        """Connect to the Lutron bridge.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Create and connect the socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            print(f"Connecting to {self.host}:{self.port}...")
            self.socket.connect((self.host, self.port))
            
            # Wait for login prompt
            result = self._read_until(b"login: ")
            
            # Send username
            self._send(self.username)
            
            # Wait for password prompt
            result = self._read_until(b"password: ")
            
            # Send password
            self._send(self.password)
            
            # Wait for command prompt
            result = self._read_until(b"GNET> ")
            print("Login successful")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            return False
    
    def _send(self, data: str) -> None:
        """Send data to the bridge.
        
        Args:
            data: Data to send
        """
        if not self.socket:
            raise ConnectionError("Not connected to bridge")
            
        with self.lock:
            self.socket.sendall(f"{data}\r\n".encode())
    
    def _read_until(self, target: bytes, timeout: int = 5) -> bytes:
        """Read from socket until target sequence is found or timeout occurs.
        
        Args:
            target: Target sequence to read until
            timeout: Timeout in seconds
            
        Returns:
            bytes: Data read from socket
            
        Raises:
            TimeoutError: If target not found within timeout
        """
        buffer = b""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                chunk = self.socket.recv(4096)
                if not chunk:
                    raise ConnectionError("Connection closed by server")
                    
                buffer += chunk
                
                if target in buffer:
                    index = buffer.find(target) + len(target)
                    return buffer[:index]
            except socket.timeout:
                continue
                
        raise TimeoutError(f"Timeout waiting for '{target.decode()}'")
    
    def load_integration_report(self, report_json: Dict[str, Any]) -> None:
        """Load zone and device data from an integration report.
        
        Args:
            report_json: JSON object with integration report data
        """
        try:
            # Extract data from integration report
            lip_data = report_json.get("LIPIdList", {})
            
            # Process zones
            zones = lip_data.get("Zones", [])
            for zone in zones:
                zone_id = str(zone.get("ID"))
                area = zone.get("Area", {}).get("Name", "Unknown")
                name = zone.get("Name", f"Zone {zone_id}")
                
                self.zones[zone_id] = {
                    "id": zone_id,
                    "name": name,
                    "area": area
                }
                
                # Keep track of areas
                if area not in self.areas:
                    self.areas[area] = []
                self.areas[area].append(zone_id)
            
            # Process devices
            devices = lip_data.get("Devices", [])
            for device in devices:
                device_id = str(device.get("ID"))
                area = device.get("Area", {}).get("Name", "Unknown")
                name = device.get("Name", f"Device {device_id}")
                buttons = device.get("Buttons", [])
                
                self.devices[device_id] = {
                    "id": device_id,
                    "name": name,
                    "area": area,
                    "buttons": buttons
                }
                
            print(f"Loaded {len(self.zones)} zones and {len(self.devices)} devices from integration report")
            
        except Exception as e:
            print(f"Error loading integration report: {e}")
    
    def send_command(self, command: str) -> str:
        """Send a command to the bridge and wait for response.
        
        Args:
            command: Command to send
            
        Returns:
            str: Response from bridge
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to bridge")
            
        try:
            with self.lock:
                # Clear any pending data
                try:
                    self.socket.settimeout(0.1)
                    while True:
                        data = self.socket.recv(4096)
                        if not data:
                            break
                except socket.timeout:
                    pass
                
                # Send the command
                self.socket.settimeout(5)
                self._send(command)
                
                # Read response until prompt
                response = self._read_until(b"GNET> ")
                return response.decode('utf-8')
                
        except Exception as e:
            print(f"Error sending command: {e}")
            raise
    
    def set_zone_level(self, zone_id: str, level: float) -> bool:
        """Set a zone to the specified level.
        
        Args:
            zone_id: ID of the zone to control
            level: Light level (0-100)
            
        Returns:
            bool: True if command was sent successfully
        """
        if not zone_id in self.zones:
            print(f"Unknown zone ID: {zone_id}")
            return False
            
        # Ensure level is within bounds
        level = max(0.0, min(100.0, level))
        
        try:
            # Format: #OUTPUT,<id>,1,<level>
            command = f"#OUTPUT,{zone_id},1,{level:.2f}"
            response = self.send_command(command)
            
            # Success!
            print(f"Set zone {zone_id} ({self.zones[zone_id]['name']}) to {level:.2f}%")
            return True
            
        except Exception as e:
            print(f"Error setting zone level: {e}")
            return False
    
    def close(self) -> None:
        """Close the connection to the bridge."""
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            
        print("Connection closed")


def main():
    """Main function to run the script from the command line."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Control Lutron Caseta devices via Telnet')
    parser.add_argument('command', choices=['list', 'on', 'off', 'set'], help='Command to execute')
    parser.add_argument('--ip', '-i', required=True, help='IP address of the Lutron bridge')
    parser.add_argument('--zone', '-z', help='Zone ID to control')
    parser.add_argument('--level', '-l', type=float, default=100.0, help='Level to set (0-100)')
    parser.add_argument('--report', '-r', help='Path to integration report JSON file')
    args = parser.parse_args()
    
    # Create bridge instance
    bridge = LutronBridge(args.ip)
    
    try:
        # Connect to the bridge
        if not bridge.connect():
            print("Failed to connect to bridge")
            return 1
        
        # Load integration report
        if args.report:
            with open(args.report, 'r') as f:
                report = json.load(f)
                bridge.load_integration_report(report)
        else:
            # Sample data from the provided report
            report_data = {
                "LIPIdList": {
                    "Zones": [
                        {"ID": 4, "Name": "Lamp Post", "Area": {"Name": "Exterior"}},
                        {"ID": 5, "Name": "Sconces 1", "Area": {"Name": "Exterior"}},
                        {"ID": 6, "Name": "Sconces 2", "Area": {"Name": "Exterior"}},
                        {"ID": 7, "Name": "Sconces 3", "Area": {"Name": "Exterior"}},
                        {"ID": 10, "Name": "Bay Window Lights", "Area": {"Name": "Master Bedroom"}},
                        {"ID": 12, "Name": "Cove Lights Street", "Area": {"Name": "Office"}},
                        {"ID": 13, "Name": "Cove Lights Northgate", "Area": {"Name": "Office"}},
                        {"ID": 15, "Name": "Right Patio", "Area": {"Name": "Patio"}},
                        {"ID": 16, "Name": "Left Patio", "Area": {"Name": "Patio"}},
                        {"ID": 20, "Name": "Closet Light", "Area": {"Name": "Master Bedroom"}},
                        {"ID": 21, "Name": "Hallway Lights", "Area": {"Name": "Master Bedroom"}},
                        {"ID": 23, "Name": "Main Lights 1", "Area": {"Name": "Front Foyer"}},
                        {"ID": 24, "Name": "Main Lights 2", "Area": {"Name": "Front Foyer"}},
                        {"ID": 14, "Name": "Plug In Dimmer", "Area": {"Name": "Outside"}},
                        {"ID": 26, "Name": "Pool Light", "Area": {"Name": "Pool"}},
                        {"ID": 27, "Name": "Sink Light", "Area": {"Name": "Kitchen"}},
                        {"ID": 2, "Name": "Hallway", "Area": {"Name": "Front Foyer"}},
                        {"ID": 28, "Name": "Main Lights", "Area": {"Name": "Front Room"}},
                        {"ID": 29, "Name": "Light Bar", "Area": {"Name": "Dining Room"}},
                        {"ID": 30, "Name": "Island Pendants", "Area": {"Name": "Kitchen"}},
                        {"ID": 32, "Name": "Main Lights", "Area": {"Name": "Office"}},
                        {"ID": 33, "Name": "Main Lights", "Area": {"Name": "Kitchen"}},
                        {"ID": 34, "Name": "Cove Lights", "Area": {"Name": "Living Room"}},
                        {"ID": 35, "Name": "Vanity Lights", "Area": {"Name": "Master Bathroom"}},
                        {"ID": 36, "Name": "Bath Lights", "Area": {"Name": "Master Bathroom"}},
                        {"ID": 37, "Name": "Val Closet", "Area": {"Name": "Master Bedroom"}},
                        {"ID": 39, "Name": "Main Lights", "Area": {"Name": "Hallway"}},
                        {"ID": 31, "Name": "Island Lights", "Area": {"Name": "Kitchen"}},
                        {"ID": 41, "Name": "Main Lights", "Area": {"Name": "Dining Room"}},
                        {"ID": 42, "Name": "Ceiling Fan Light", "Area": {"Name": "Nursery"}},
                        {"ID": 44, "Name": "Back Porch Lights", "Area": {"Name": "Pool"}},
                        {"ID": 45, "Name": "Sconces", "Area": {"Name": "Patio"}},
                        {"ID": 46, "Name": "Main Lights", "Area": {"Name": "Guest Bathroom"}},
                        {"ID": 47, "Name": "Vanity Lights", "Area": {"Name": "Guest Bathroom"}},
                        {"ID": 48, "Name": "Inside Light", "Area": {"Name": "Pool"}},
                        {"ID": 49, "Name": "Main Lights", "Area": {"Name": "Garage"}},
                        {"ID": 50, "Name": "Sconces 4 Apartment", "Area": {"Name": "Exterior"}}
                    ]
                }
            }
            bridge.load_integration_report(report_data)
        
        # Execute the requested command
        if args.command == 'list':
            # List all zones
            print("\n=== Zones ===")
            sorted_areas = sorted(bridge.areas.keys())
            for area in sorted_areas:
                print(f"\nArea: {area}")
                for zone_id in bridge.areas[area]:
                    zone = bridge.zones[zone_id]
                    print(f"  Zone {zone_id}: {zone['name']}")
                
        elif args.command == 'on' and args.zone:
            # Turn a zone on (100%)
            bridge.set_zone_level(args.zone, 100.0)
            
        elif args.command == 'off' and args.zone:
            # Turn a zone off (0%)
            bridge.set_zone_level(args.zone, 0.0)
            
        elif args.command == 'set' and args.zone:
            # Set a zone to a specific level
            bridge.set_zone_level(args.zone, args.level)
            
        else:
            print("Invalid command or missing zone ID")
            return 1
            
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    finally:
        bridge.close()


if __name__ == "__main__":
    sys.exit(main()) 