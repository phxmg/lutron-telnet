#!/usr/bin/env python3
"""
Lutron Monitor - Monitor real-time activity on the Lutron bridge
"""
import argparse
import sys
import time
import threading
import socket

# Hardcoded bridge IP address
DEFAULT_BRIDGE_IP = "192.168.49.91"
DEFAULT_TIMEOUT = 60  # Longer timeout for monitoring

def parse_args():
    parser = argparse.ArgumentParser(description='Monitor Lutron bridge activity')
    parser.add_argument('--ip', '-i', default=DEFAULT_BRIDGE_IP, 
                        help=f'IP address of the Lutron bridge (default: {DEFAULT_BRIDGE_IP})')
    parser.add_argument('--timeout', '-t', type=int, default=DEFAULT_TIMEOUT, 
                        help=f'Connection timeout in seconds (default: {DEFAULT_TIMEOUT})')
    return parser.parse_args()

def main():
    args = parse_args()
    
    print(f"\nLutron Bridge Monitor")
    print(f"-------------------")
    print(f"IP: {args.ip}")
    print(f"Timeout: {args.timeout} seconds")
    print(f"\nConnecting and enabling monitoring mode...")
    
    try:
        # Create socket with longer timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(args.timeout)
        sock.connect((args.ip, 23))
        
        # Login sequence
        def wait_for(target):
            buffer = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                if target in buffer:
                    return True
            return False
        
        # Wait for login prompt
        if not wait_for(b"login: "):
            print("Failed to get login prompt")
            return 1
        
        # Send username
        sock.sendall(b"lutron\r\n")
        time.sleep(0.1)
        
        # Wait for password prompt
        if not wait_for(b"password: "):
            print("Failed to get password prompt")
            return 1
        
        # Send password
        sock.sendall(b"integration\r\n")
        time.sleep(0.1)
        
        # Wait for GNET prompt
        if not wait_for(b"GNET> "):
            print("Failed to get GNET prompt")
            return 1
        
        print("Connected successfully!")
        
        # Enable monitoring mode for all events
        print("Enabling monitoring mode...")
        sock.sendall(b"#MONITORING,255,1\r\n")
        time.sleep(0.1)
        
        # Set non-blocking mode for continuous reading
        sock.setblocking(0)
        sock.settimeout(0.1)
        
        print("\n📊 MONITORING ACTIVE 📊")
        print("Press Ctrl+C to stop monitoring\n")
        
        # Monitoring loop
        buffer = b""
        try:
            while True:
                try:
                    data = sock.recv(4096)
                    if data:
                        buffer += data
                        
                        # Process any complete messages in the buffer
                        lines = buffer.split(b'\r\n')
                        
                        # Keep the last incomplete line in the buffer
                        buffer = lines[-1]
                        
                        # Process complete lines
                        for line in lines[:-1]:
                            if line:
                                decoded = line.decode('utf-8', errors='replace').strip()
                                # Filter out noise and print meaningful events
                                if decoded and not decoded.startswith("GNET>"):
                                    timestamp = time.strftime("%H:%M:%S")
                                    print(f"[{timestamp}] {decoded}")
                    
                except socket.timeout:
                    # This is normal for non-blocking socket with timeout
                    pass
                except BlockingIOError:
                    # No data available right now
                    pass
                
                # Small delay to prevent CPU spinning
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        
        # Disable monitoring
        sock.setblocking(1)
        sock.settimeout(args.timeout)
        print("\nDisabling monitoring...")
        sock.sendall(b"#MONITORING,255,0\r\n")
        
        # Close the socket
        sock.close()
        print("Connection closed")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 