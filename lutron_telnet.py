#!/usr/bin/env python3

import socket
import time
import sys
import threading
import re
import logging
import json
from typing import Dict, List, Optional, Tuple, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("lutron_telnet")

class LutronTelnet:
    """
    Interface to Lutron Caseta Smart Bridge / RA2 Select Main Repeater using Telnet
    """

    def __init__(
        self, 
        host: str, 
        port: int = 23, 
        username: str = "lutron", 
        password: str = "integration"
    ):
        """Initialize the Lutron Telnet connection.
        
        Args:
            host: IP address of the Lutron bridge
            port: Telnet port (default 23)
            username: Telnet username (default 'lutron')
            password: Telnet password (default 'integration')
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        self.socket = None
        self.reader_thread = None
        self.running = False
        self.buffer = b""
        self.zones = {}
        self.scenes = {}
        self.areas = {}
        self.devices = {}
        self.callbacks = []
        self.monitoring = False
        
    def connect(self) -> bool:
        """Establish connection to the bridge.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        try:
            # Create the socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            
            # Connect to the bridge
            logger.info(f"Connecting to {self.host}:{self.port}")
            self.socket.connect((self.host, self.port))
            
            # Wait for login prompt and send username
            data = self._read_until(b"login: ")
            self._send_command(self.username)
            
            # Wait for password prompt and send password
            data = self._read_until(b"password: ")
            self._send_command(self.password)
            
            # Wait for command prompt
            data = self._read_until(b"GNET> ")
            logger.info("Login successful")
            
            # Start reader thread
            self.running = True
            self.reader_thread = threading.Thread(target=self._reader_thread)
            self.reader_thread.daemon = True
            self.reader_thread.start()
            
            # Get device and zone information
            self._discover_devices()
            
            return True
            
        except (socket.error, TimeoutError) as e:
            logger.error(f"Connection error: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            return False
    
    def _reader_thread(self):
        """Thread to continuously read from the socket."""
        try:
            self.socket.settimeout(None)  # Set socket to blocking mode
            while self.running:
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        logger.error("Connection closed by server")
                        break
                    
                    self.buffer += data
                    self._process_buffer()
                    
                except socket.error as e:
                    logger.error(f"Socket error in reader thread: {e}")
                    break
        finally:
            self.running = False
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            logger.info("Reader thread stopped")
    
    def _process_buffer(self):
        """Process the received data buffer."""
        while b'\r\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\r\n', 1)
            try:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line and not decoded_line.startswith("GNET>"):
                    self._process_line(decoded_line)
            except UnicodeDecodeError:
                logger.error(f"Could not decode line: {line}")
    
    def _process_line(self, line: str):
        """Process a received line of data."""
        logger.debug(f"Processing line: {line}")
        
        # If line starts with ~ it's a response or event
        if line.startswith("~"):
            parts = line.split(",")
            if len(parts) < 2:
                return
                
            command_type = parts[0]
            
            # Output status update
            if command_type == "~OUTPUT":
                try:
                    output_id = parts[1]
                    action = parts[2]
                    value = parts[3] if len(parts) > 3 else None
                    self._handle_output_event(output_id, action, value)
                except IndexError:
                    pass
                    
            # Device status update
            elif command_type == "~DEVICE":
                try:
                    device_id = parts[1]
                    component_id = parts[2]
                    action = parts[3]
                    self._handle_device_event(device_id, component_id, action)
                except IndexError:
                    pass
                    
            # Error message
            elif command_type == "~ERROR":
                logger.error(f"Bridge error: {line}")
        
        # Process for any registered callbacks
        for callback in self.callbacks:
            try:
                callback(line)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
    
    def _handle_output_event(self, output_id: str, action: str, value: Optional[str]):
        """Handle an output status update event."""
        if output_id in self.zones:
            zone = self.zones[output_id]
            zone['current_level'] = float(value) if value is not None else None
            logger.info(f"Zone {output_id} ({zone.get('name', 'Unknown')}) updated to level {value}")
            
    def _handle_device_event(self, device_id: str, component_id: str, action: str):
        """Handle a device event."""
        device_info = self.devices.get(device_id, {"id": device_id, "name": f"Device {device_id}"})
        logger.info(f"Device {device_id} ({device_info.get('name', 'Unknown')}) component {component_id} action {action}")
        
    def add_callback(self, callback: Callable[[str], None]):
        """Add a callback to be called for each line of data received.
        
        Args:
            callback: Function to call with each line
        """
        self.callbacks.append(callback)
        
    def remove_callback(self, callback: Callable[[str], None]):
        """Remove a previously registered callback.
        
        Args:
            callback: Function to remove
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _send_command(self, command: str) -> None:
        """Send a command to the bridge.
        
        Args:
            command: Command to send
        """
        if self.socket:
            full_command = f"{command}\r\n"
            self.socket.sendall(full_command.encode())
        else:
            raise ConnectionError("Not connected to bridge")
    
    def _read_until(self, target: bytes, timeout: int = 5) -> bytes:
        """Read from socket until target sequence is found or timeout occurs.
        
        Args:
            target: Target sequence to read until
            timeout: Timeout in seconds
            
        Returns:
            bytes: Data read from socket including target
            
        Raises:
            TimeoutError: If target not found within timeout
        """
        buffer = b""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data = self.socket.recv(4096)
                if not data:
                    raise ConnectionError("Connection closed by server")
                buffer += data
                
                if target in buffer:
                    index = buffer.find(target) + len(target)
                    return buffer[:index]
            except socket.timeout:
                continue
        
        raise TimeoutError(f"Timeout waiting for '{target.decode()}'")
    
    def send_command(self, command: str) -> str:
        """Send a command to the bridge and return response.
        
        Args:
            command: Command to send
            
        Returns:
            str: Response from bridge
        """
        if not self.socket:
            raise ConnectionError("Not connected to bridge")
            
        # Send the command
        self._send_command(command)
        
        # Read response until prompt
        try:
            response = self._read_until(b"GNET> ")
            return response.decode('utf-8')
        except (TimeoutError, ConnectionError) as e:
            logger.error(f"Error reading response: {e}")
            raise
    
    def _discover_devices(self):
        """Query the bridge for device information."""
        try:
            # Try getting areas
            try:
                response = self.send_command("?AREA")
                self._parse_areas(response)
            except Exception as e:
                logger.warning(f"Error getting areas: {e}")
            
            # Try getting zones
            try:
                response = self.send_command("?ZONE")
                self._parse_zones(response)
            except Exception as e:
                logger.warning(f"Error getting zones: {e}")
                
            # Try getting outputs
            try:
                response = self.send_command("?OUTPUT")
                self._parse_outputs(response)
            except Exception as e:
                logger.warning(f"Error getting outputs: {e}")
                
            # Try getting devices
            try:
                response = self.send_command("?DEVICE")
                self._parse_devices(response)
            except Exception as e:
                logger.warning(f"Error getting devices: {e}")
                
            logger.info(f"Discovered {len(self.zones)} zones, {len(self.areas)} areas, {len(self.devices)} devices")
                
        except Exception as e:
            logger.error(f"Error during device discovery: {e}")
            
    def _parse_areas(self, response: str):
        """Parse area information from response.
        
        Args:
            response: Response string from bridge
        """
        lines = response.strip().split('\r\n')
        for line in lines:
            if line.startswith("~AREA"):
                parts = line.split(',')
                if len(parts) >= 3:
                    area_id = parts[1]
                    area_name = parts[2]
                    self.areas[area_id] = {
                        'id': area_id,
                        'name': area_name
                    }
    
    def _parse_zones(self, response: str):
        """Parse zone information from response.
        
        Args:
            response: Response string from bridge
        """
        lines = response.strip().split('\r\n')
        for line in lines:
            if line.startswith("~ZONE"):
                parts = line.split(',')
                if len(parts) >= 3:
                    zone_id = parts[1]
                    area_id = parts[2]
                    zone_name = parts[3] if len(parts) > 3 else "Unknown"
                    
                    area_name = self.areas.get(area_id, {}).get('name', "Unknown Area")
                    
                    self.zones[zone_id] = {
                        'id': zone_id,
                        'name': zone_name,
                        'area_id': area_id,
                        'area_name': area_name,
                        'current_level': None
                    }
    
    def _parse_outputs(self, response: str):
        """Parse output information from response.
        
        Args:
            response: Response string from bridge
        """
        lines = response.strip().split('\r\n')
        for line in lines:
            if line.startswith("~OUTPUT"):
                parts = line.split(',')
                if len(parts) >= 3:
                    output_id = parts[1]
                    zone_id = parts[2]
                    output_type = parts[3] if len(parts) > 3 else "Unknown"
                    
                    # Link output to zone if exists
                    if zone_id in self.zones:
                        self.zones[zone_id]['output_id'] = output_id
                        self.zones[zone_id]['type'] = output_type
    
    def _parse_devices(self, response: str):
        """Parse device information from response.
        
        Args:
            response: Response string from bridge
        """
        lines = response.strip().split('\r\n')
        for line in lines:
            if line.startswith("~DEVICE"):
                parts = line.split(',')
                if len(parts) >= 3:
                    device_id = parts[1]
                    device_name = parts[2] if len(parts) > 2 else "Unknown"
                    device_type = parts[3] if len(parts) > 3 else "Unknown"
                    
                    self.devices[device_id] = {
                        'id': device_id,
                        'name': device_name,
                        'type': device_type
                    }
    
    def start_monitoring(self):
        """Start monitoring for device events."""
        if self.monitoring:
            return
            
        try:
            # Enable monitoring
            response = self.send_command("#MONITORING,255,1")
            self.monitoring = True
            logger.info("Monitoring started")
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring for device events."""
        if not self.monitoring:
            return
            
        try:
            # Disable monitoring
            response = self.send_command("#MONITORING,255,0")
            self.monitoring = False
            logger.info("Monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    def get_zones(self) -> Dict:
        """Get all zones (light/shade controls).
        
        Returns:
            Dict: Dictionary of zone information
        """
        return self.zones
    
    def get_devices(self) -> Dict:
        """Get all devices.
        
        Returns:
            Dict: Dictionary of device information
        """
        return self.devices
    
    def get_areas(self) -> Dict:
        """Get all areas.
        
        Returns:
            Dict: Dictionary of area information
        """
        return self.areas
    
    def set_zone_level(self, zone_id: str, level: float) -> bool:
        """Set a zone level (0-100).
        
        Args:
            zone_id: Zone ID to control
            level: Level to set (0-100)
            
        Returns:
            bool: True if command was sent successfully
        """
        if not self.socket:
            raise ConnectionError("Not connected to bridge")
            
        # Ensure level is within bounds
        level = max(0.0, min(100.0, level))
        
        try:
            # Send command to set level
            command = f"#OUTPUT,{zone_id},1,{level}"
            self.send_command(command)
            
            # Update local state
            if zone_id in self.zones:
                self.zones[zone_id]['current_level'] = level
                
            return True
        except Exception as e:
            logger.error(f"Error setting zone level: {e}")
            return False
    
    def close(self):
        """Close the connection to the bridge."""
        self.running = False
        
        if self.monitoring:
            try:
                self.stop_monitoring()
            except:
                pass
                
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=1.0)
            
        logger.info("Connection closed")


def main():
    """Main function for command-line use."""
    if len(sys.argv) < 2:
        print("Usage: lutron_telnet.py <bridge_ip>")
        sys.exit(1)
    
    bridge_ip = sys.argv[1]
    lutron = LutronTelnet(bridge_ip)
    
    try:
        # Connect to bridge
        if not lutron.connect():
            print("Failed to connect to bridge")
            sys.exit(1)
        
        # Start monitoring
        lutron.start_monitoring()
        
        # Print zones
        zones = lutron.get_zones()
        if zones:
            print("\nZones:")
            for zone_id, zone in zones.items():
                print(f"  Zone {zone_id}: {zone.get('name')} ({zone.get('area_name')})")
        else:
            print("\nNo zones found")
        
        # Print devices
        devices = lutron.get_devices()
        if devices:
            print("\nDevices:")
            for device_id, device in devices.items():
                print(f"  Device {device_id}: {device.get('name')} ({device.get('type', 'Unknown type')})")
        else:
            print("\nNo devices found")
        
        # Wait for user to quit
        print("\nMonitoring for events. Press Ctrl+C to quit.")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        lutron.close()


if __name__ == "__main__":
    main() 