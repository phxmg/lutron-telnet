#!/usr/bin/env python3

import socket
import time
import sys

class SimpleTelnet:
    def __init__(self, host, port=23):
        self.host = host
        self.port = port
        self.socket = None
        self.buffer = b""
        
    def connect(self):
        """Establish a connection and login"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            
            # Wait for login prompt
            data = self.read_until(b"login: ")
            print(f"Connected to {self.host}")
            
            # Send username
            self.send("lutron")
            
            # Wait for password prompt
            data = self.read_until(b"password: ")
            
            # Send password
            self.send("integration")
            
            # Wait for successful login confirmation
            data = self.read_until(b"GNET> ")
            print("Login successful\n")
            
            return True
        except socket.error as e:
            print(f"Connection error: {e}")
            return False
    
    def send(self, command):
        """Send a command with proper line ending"""
        if self.socket:
            full_command = f"{command}\r\n"
            self.socket.sendall(full_command.encode())
    
    def read_until(self, target, timeout=5):
        """Read from socket until target sequence is found or timeout occurs"""
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
        """Send a command and get response until prompt"""
        print(f"Sending: {command}")
        self.send(command)
        response = self.read_until(b"GNET> ")
        print(f"Response: {response.decode()}")
        return response.decode()
    
    def close(self):
        """Close the connection"""
        if self.socket:
            self.socket.close()
            self.socket = None
            
def test_caseta_commands(host):
    """Test various Caseta-specific commands"""
    telnet = SimpleTelnet(host)
    
    try:
        if telnet.connect():
            # Try monitoring mode first
            print("=== Testing Monitoring Mode ===")
            response = telnet.send_command("#MONITORING,255,1")
            
            # Try specific Caseta commands
            print("\n=== Testing Lutron Caseta Commands ===")
            
            # Try to get information about bridge itself
            print("\n-- Bridge Information --")
            telnet.send_command("#HELP")
            
            # Try different command syntaxes for listing devices
            print("\n-- Device Listing Tests --")
            
            # Try to get device list with various syntaxes
            telnet.send_command("?DEVICELIST")
            telnet.send_command("?ENUMDEVICE")
            telnet.send_command("?GROUPLIST")
            
            # Try a common command for RadioRA2 systems
            telnet.send_command("#MONITOR")
            
            # Try Caseta-specific LEAP protocol commands
            print("\n-- Caseta LEAP Protocol Tests --")
            telnet.send_command("/api/discovery")
            telnet.send_command("/api/devices")
            
            # Try Lutron HomeWorks command format
            print("\n-- HomeWorks Command Format Tests --")
            telnet.send_command("DLUP")  # Request device list update
            
            # Try some direct hardware manipulation commands
            print("\n-- Direct Hardware Commands --")
            telnet.send_command("?HARDWARE")
            
            # Try diagnostics
            print("\n-- Diagnostics Commands --")
            telnet.send_command("?LOG")
            telnet.send_command("?STATUS")
            
            # Try button press for device ID 1
            print("\n-- Button Press Test --")
            telnet.send_command("#BUTTON,1,3,1")  # device 1, button 3, action press
            
            print("\n=== End of Caseta Command Tests ===")
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        telnet.close()
        print("\nConnection closed")
        
if __name__ == "__main__":
    # Use command line arg for IP if provided
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.49.91"
    test_caseta_commands(host) 