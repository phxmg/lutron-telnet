#!/usr/bin/env python3

import socket
import time
import sys
import json
import argparse

class LutronQuick:
    """Simplified Lutron Telnet controller with quick commands."""
    
    def __init__(self, host, port=23, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
    
    def connect(self):
        """Connect to the Lutron bridge with a shorter timeout."""
        try:
            # Create socket with timeout
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            
            # Connect
            print(f"Connecting to {self.host}:{self.port}...")
            self.socket.connect((self.host, self.port))
            
            # Wait for login prompt
            data = self._read_with_timeout(b"login: ")
            if not data:
                print("Didn't receive login prompt")
                return False
                
            # Send username
            self._send("lutron")
            
            # Wait for password prompt
            data = self._read_with_timeout(b"password: ")
            if not data:
                print("Didn't receive password prompt")
                return False
                
            # Send password
            self._send("integration")
            
            # Wait for prompt
            data = self._read_with_timeout(b"GNET> ")
            if not data:
                print("Didn't receive command prompt")
                return False
                
            print("Connected successfully")
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            return False
    
    def _send(self, data):
        """Send a command to the bridge."""
        if self.socket:
            try:
                self.socket.sendall(f"{data}\r\n".encode())
                # Small delay after sending
                time.sleep(0.1)
            except Exception as e:
                print(f"Send error: {e}")
                return False
            return True
        return False
    
    def _read_with_timeout(self, target=None, timeout=None):
        """Read data with timeout, optionally until target is found."""
        if timeout is None:
            timeout = self.timeout
            
        if not self.socket:
            return None
            
        buffer = b""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                    
                buffer += data
                
                # If we're looking for a specific target
                if target and target in buffer:
                    return buffer
                    
                # If not looking for a target, return whatever we got
                if not target:
                    return buffer
                    
            except socket.timeout:
                # Timeout reading, but we may still have partial data
                break
            except Exception as e:
                print(f"Read error: {e}")
                break
                
        return buffer if buffer else None
    
    def send_command(self, command, wait_response=True):
        """Send a command and optionally wait for response."""
        if not self.socket:
            print("Not connected")
            return None
            
        # Send the command
        success = self._send(command)
        if not success:
            return None
            
        if wait_response:
            # Wait for prompt to return
            response = self._read_with_timeout(b"GNET> ")
            if response:
                return response.decode('utf-8', errors='replace')
        
        return ""
    
    def set_light(self, zone_id, level):
        """Set a light zone to a specific level."""
        # Ensure level is in range
        level = max(0.0, min(100.0, level))
        
        # Format command
        command = f"#OUTPUT,{zone_id},1,{level:.2f}"
        
        # Send it
        print(f"Setting zone {zone_id} to {level:.1f}%")
        result = self.send_command(command, wait_response=True)
        
        # Check for error
        if result and "ERROR" in result:
            print(f"Command error: {result}")
            return False
        
        return True
    
    def close(self):
        """Close the connection."""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("Connection closed")

def main():
    parser = argparse.ArgumentParser(description='Quick Lutron light control')
    parser.add_argument('--ip', '-i', required=True, help='Bridge IP address')
    parser.add_argument('--zone', '-z', type=str, required=True, help='Zone ID to control')
    parser.add_argument('--level', '-l', type=float, default=100.0, help='Light level (0-100)')
    parser.add_argument('--timeout', '-t', type=int, default=3, help='Connection timeout')
    
    args = parser.parse_args()
    
    # Create controller
    controller = LutronQuick(args.ip, timeout=args.timeout)
    
    try:
        # Connect
        if not controller.connect():
            print("Failed to connect")
            return 1
        
        # Control the light
        success = controller.set_light(args.zone, args.level)
        
        if success:
            print(f"Successfully sent command to zone {args.zone}")
        else:
            print(f"Failed to control zone {args.zone}")
            
    finally:
        # Always close the connection
        controller.close()
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 