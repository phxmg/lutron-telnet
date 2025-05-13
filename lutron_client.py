#!/usr/bin/env python3

import socket
import time
import re
import sys

class LutronBridge:
    def __init__(self, host, port=23, username="lutron", password="integration"):
        """
        Initialize a connection to a Lutron Caseta Smart Bridge Pro.
        
        Args:
            host (str): IP address of the bridge
            port (int): Port number (default is 23 for Telnet)
            username (str): Username for authentication (default is "lutron")
            password (str): Password for authentication (default is "integration")
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socket = None
        self.buffer = b""
    
    def connect(self):
        """Establish connection to the bridge."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            
            # Wait for login prompt
            response = self.read_until(b"login: ")
            print(f"Connected to {self.host}")
            
            # Send username
            self.socket.sendall(f"{self.username}\r\n".encode())
            
            # Wait for password prompt
            response = self.read_until(b"password: ")
            
            # Send password
            self.socket.sendall(f"{self.password}\r\n".encode())
            
            # Wait for successful login confirmation
            response = self.read_until(b"GNET> ")
            print("Login successful")
            
            return True
        except socket.error as e:
            print(f"Connection error: {e}")
            return False
    
    def read_until(self, target, timeout=5):
        """
        Read from socket until target sequence is found or timeout occurs.
        
        Args:
            target (bytes): Target sequence to read until
            timeout (int): Timeout in seconds
            
        Returns:
            bytes: Data read from socket
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data = self.socket.recv(4096)
                if not data:
                    raise ConnectionError("Connection closed by server")
                self.buffer += data
                
                if target in self.buffer:
                    response, self.buffer = self.buffer.split(target, 1)
                    return response + target
            except socket.timeout:
                continue
        
        raise TimeoutError(f"Timeout waiting for '{target.decode()}'")
    
    def send_command(self, command):
        """
        Send a command to the bridge.
        
        Args:
            command (str): Command to send
            
        Returns:
            str: Response from bridge
        """
        full_command = f"{command}\r\n"
        self.socket.sendall(full_command.encode())
        response = self.read_until(b"GNET> ")
        return response.decode()
    
    def get_devices(self):
        """
        Get a list of all devices.
        
        Returns:
            list: List of device information
        """
        response = self.send_command("?DEVICE")
        devices = []
        # Process the response to extract device information
        lines = response.strip().split('\r\n')
        for line in lines:
            # Skip the command echo and the prompt
            if line.startswith("?DEVICE") or line.startswith("GNET>") or not line.strip():
                continue
            
            # Parse device information
            # Typical format: ~DEVICE,<device_id>,<device_name>,<device_type>
            if line.startswith("~DEVICE"):
                parts = line.split(',')
                if len(parts) >= 3:
                    device_id = parts[1]
                    device_name = parts[2] if len(parts) > 2 else "Unknown"
                    device_type = parts[3] if len(parts) > 3 else "Unknown"
                    devices.append({
                        'id': device_id,
                        'name': device_name,
                        'type': device_type
                    })
        
        return devices
    
    def get_zones(self):
        """
        Get a list of all zones (controllable entities).
        
        Returns:
            list: List of zone information
        """
        response = self.send_command("?AREA")
        areas = {}
        # First get all areas to use for zone mapping
        lines = response.strip().split('\r\n')
        for line in lines:
            if line.startswith("~AREA"):
                parts = line.split(',')
                if len(parts) >= 3:
                    area_id = parts[1]
                    area_name = parts[2]
                    areas[area_id] = area_name
        
        # Now get all zones
        response = self.send_command("?ZONE")
        zones = []
        lines = response.strip().split('\r\n')
        for line in lines:
            if line.startswith("~ZONE"):
                parts = line.split(',')
                if len(parts) >= 3:
                    zone_id = parts[1]
                    area_id = parts[2]
                    zone_name = parts[3] if len(parts) > 3 else "Unknown"
                    area_name = areas.get(area_id, "Unknown Area")
                    zones.append({
                        'id': zone_id,
                        'name': zone_name,
                        'area_id': area_id,
                        'zone_name': zone_name
                    })
        
        return zones
    
    def get_outputs(self):
        """
        Get a list of all outputs (the actual controls for lights, shades, etc.).
        
        Returns:
            list: List of output information
        """
        response = self.send_command("?OUTPUT")
        outputs = []
        lines = response.strip().split('\r\n')
        for line in lines:
            if line.startswith("~OUTPUT"):
                parts = line.split(',')
                if len(parts) >= 3:
                    output_id = parts[1]
                    zone_id = parts[2]
                    output_type = parts[3] if len(parts) > 3 else "Unknown"
                    outputs.append({
                        'id': output_id,
                        'zone_id': zone_id,
                        'type': output_type
                    })
        
        return outputs
    
    def get_controllable_entities(self):
        """
        Get a comprehensive list of all controllable entities with their details.
        
        Returns:
            list: List of controllable entities with details
        """
        zones = self.get_zones()
        outputs = self.get_outputs()
        
        # Map outputs to zones
        zone_output_map = {}
        for output in outputs:
            zone_id = output['zone_id']
            if zone_id not in zone_output_map:
                zone_output_map[zone_id] = []
            zone_output_map[zone_id].append(output)
        
        # Create comprehensive entity list
        entities = []
        for zone in zones:
            zone_id = zone['id']
            entity = {
                'zone_id': zone_id,
                'name': zone['name'],
                'zone_name': zone['zone_name'],
                'area_id': zone['area_id'],
                'outputs': zone_output_map.get(zone_id, [])
            }
            entities.append(entity)
        
        return entities
    
    def close(self):
        """Close the connection."""
        if self.socket:
            self.socket.close()

def print_entities(entities):
    """
    Pretty print the controllable entities.
    
    Args:
        entities (list): List of entities
    """
    print("\n=== Controllable Entities ===")
    for entity in entities:
        print(f"\nZone: {entity['zone_name']} (ID: {entity['zone_id']})")
        print(f"  Area: {entity['name']} (ID: {entity['area_id']})")
        print("  Outputs:")
        for output in entity['outputs']:
            print(f"    - Output ID: {output['id']}, Type: {output['type']}")

def main():
    # Check if IP address is provided as command line argument
    if len(sys.argv) > 1:
        bridge_ip = sys.argv[1]
    else:
        bridge_ip = "192.168.49.91"  # Default to provided IP
    
    bridge = LutronBridge(bridge_ip)
    
    try:
        if bridge.connect():
            print("\nRetrieving entities...")
            entities = bridge.get_controllable_entities()
            print_entities(entities)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        bridge.close()
        print("\nConnection closed")

if __name__ == "__main__":
    main() 