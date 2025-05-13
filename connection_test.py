#!/usr/bin/env python3

import socket
import time
import sys

def dump_hex(data):
    """Print data in hex format for debugging"""
    if isinstance(data, str):
        data = data.encode()
    hex_data = ' '.join(f'{b:02x}' for b in data)
    print(f"HEX: {hex_data}")

def test_raw_connection(host="192.168.49.91", port=23):
    """Test raw telnet connection without assumptions about protocol"""
    print(f"Connecting to {host}:{port}...")
    
    sock = None
    try:
        # Create socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        print(f"Connected to {host}:{port}")
        
        # Wait for initial data
        print("\nWaiting for initial data...")
        time.sleep(1)
        
        # Read any initial data
        buffer = b""
        try:
            while True:
                sock.settimeout(2)
                data = sock.recv(4096)
                if not data:
                    break
                buffer += data
                print(f"Received {len(data)} bytes")
                print(f"Data: {data.decode('utf-8', errors='replace')}")
                dump_hex(data)
        except socket.timeout:
            print("Initial read timed out (this is normal if no more data)")
        
        # Send username
        print("\nSending username: lutron")
        sock.sendall(b"lutron\r\n")
        time.sleep(1)
        
        # Read response after username
        buffer = b""
        try:
            while True:
                sock.settimeout(2)
                data = sock.recv(4096)
                if not data:
                    break
                buffer += data
                print(f"Received {len(data)} bytes after sending username")
                print(f"Data: {data.decode('utf-8', errors='replace')}")
                dump_hex(data)
        except socket.timeout:
            print("Read after username timed out")
        
        # Send password
        print("\nSending password: integration")
        sock.sendall(b"integration\r\n")
        time.sleep(1)
        
        # Read response after password
        buffer = b""
        try:
            while True:
                sock.settimeout(2)
                data = sock.recv(4096)
                if not data:
                    break
                buffer += data
                print(f"Received {len(data)} bytes after sending password")
                print(f"Data: {data.decode('utf-8', errors='replace')}")
                dump_hex(data)
        except socket.timeout:
            print("Read after password timed out")
        
        # Send a basic command
        print("\nSending a test command: ?")
        sock.sendall(b"?\r\n")
        time.sleep(1)
        
        # Read response after test command
        buffer = b""
        try:
            while True:
                sock.settimeout(2)
                data = sock.recv(4096)
                if not data:
                    break
                buffer += data
                print(f"Received {len(data)} bytes after sending test command")
                print(f"Data: {data.decode('utf-8', errors='replace')}")
                dump_hex(data)
        except socket.timeout:
            print("Read after test command timed out")
            
    except socket.error as e:
        print(f"Socket error: {e}")
        return False
    finally:
        if sock:
            sock.close()
            print("Connection closed")
    
    return True

if __name__ == "__main__":
    # Use command line arg for IP if provided
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.49.91"
    test_raw_connection(host) 