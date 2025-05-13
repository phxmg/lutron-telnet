#!/usr/bin/env python3

import socket
import time
import sys

def monitor_bridge(host, port=23, duration=30):
    """
    Simple monitor that just listens for any events from the bridge.
    Many Lutron systems broadcast state changes automatically.
    
    Args:
        host (str): IP address of the bridge
        port (int): Port to connect to
        duration (int): How long to listen in seconds
    """
    print(f"Connecting to {host}:{port} to monitor for {duration} seconds...")
    
    sock = None
    try:
        # Connect to the bridge
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        # Wait for login prompt
        buffer = b""
        while b"login: " not in buffer:
            data = sock.recv(4096)
            buffer += data
            if not data:
                raise ConnectionError("Connection closed unexpectedly")
        
        print("Connected, sending credentials...")
        
        # Send username
        sock.sendall(b"lutron\r\n")
        
        # Wait for password prompt
        buffer = b""
        while b"password: " not in buffer:
            data = sock.recv(4096)
            buffer += data
            if not data:
                raise ConnectionError("Connection closed unexpectedly")
        
        # Send password
        sock.sendall(b"integration\r\n")
        
        # Wait for GNET prompt
        buffer = b""
        while b"GNET> " not in buffer:
            data = sock.recv(4096)
            buffer += data
            if not data:
                raise ConnectionError("Connection closed unexpectedly")
        
        print("Login successful, monitoring for events...")
        
        # Set socket to non-blocking to continuously read
        sock.setblocking(0)
        
        # Monitor for specified duration
        start_time = time.time()
        received_data = False
        
        while time.time() - start_time < duration:
            try:
                # Try to read data
                data = sock.recv(4096)
                
                if data:
                    received_data = True
                    print(f"\nReceived data at {time.time() - start_time:.2f} seconds:")
                    print(f"Raw: {data}")
                    try:
                        decoded = data.decode('utf-8', errors='replace')
                        print(f"Decoded: {decoded}")
                    except:
                        pass
            except socket.error:
                # No data available, just wait
                print(".", end="", flush=True)
                time.sleep(1)
        
        if not received_data:
            print("\nNo data received during monitoring period.")
            print("Try interacting with your Lutron system while monitoring to generate events.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if sock:
            sock.close()
        print("\nMonitoring complete, connection closed.")

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.49.91"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    monitor_bridge(host, duration=duration) 