# Lutron Caseta Telnet Integration Guide

This guide documents the process for integrating with Lutron Caseta Smart Bridge Pro devices using the Telnet integration protocol. It covers key insights, challenges, and solutions discovered during implementation.

## Bridge Requirements

- **Compatible Devices**: 
  - Lutron Caseta Smart Bridge Pro (L-BDGPRO2-WH)
  - Ra2 Select Main Repeater

- **Prerequisites**:
  - Telnet integration must be explicitly enabled in the Lutron app
  - Bridge must have a static IP address

## Connection Details

### Basic Connection Information

- **Protocol**: Telnet
- **Port**: 23 (standard Telnet port)
- **Authentication**: Username/password
  - Default username: `lutron`
  - Default password: `integration`

### Connection Process

1. Establish TCP socket connection to bridge IP on port 23
2. Wait for `login:` prompt
3. Send username (`lutron`) followed by CR+LF (`\r\n`)
4. Wait for `password:` prompt
5. Send password (`integration`) followed by CR+LF
6. Wait for `GNET>` prompt (indicates successful login)

### Critical Insights

- **Short Timeouts**: Use short timeouts (3-5 seconds) to prevent hanging
- **Read Until**: Always read until a specific terminator sequence (`login:`, `password:`, `GNET>`)
- **Buffer Management**: Accumulate received data in a buffer until terminator is found
- **Prompt Detection**: The `GNET>` string signals command completion
- **Line Endings**: Always use CR+LF (`\r\n`) as line terminators
- **Drain Socket**: Clear any pending data before sending new commands

## Command Structure

### Command Format

Commands follow these general patterns:

1. **Query commands**: Start with `?`
   - Example: `?DEVICE` - Query devices
   - Example: `?AREA` - Query areas
   - Example: `?ZONE` - Query zones

2. **Action commands**: Start with `#` 
   - Example: `#OUTPUT,{zone_id},1,{level}` - Set light level

3. **Monitoring**: Enable with `#MONITORING,255,1`

### Light Control Commands

- **Light Level Control**: `#OUTPUT,{zone_id},1,{level}`
  - `zone_id`: The numerical ID of the zone (light/device)
  - `level`: A decimal number from 0.0 to 100.0
    - 0.0 = Off
    - 100.0 = Full brightness
    - Intermediate values = Dimmed

### Response Format

- Responses to query commands start with `~`
- Error responses start with `~ERROR`
- Common errors:
  - `~ERROR,Enum=(6, 0x00000006)` - Invalid command or command not recognized
  - `~ERROR,Enum=(1, 0x00000001)` - General command error

## Implementation Challenges & Solutions

### Connection Timeouts

**Challenge**: The previous implementations waited indefinitely for responses, causing hangs.

**Solution**: 
- Use short timeouts (3-5 seconds)
- Return partial data if timeout occurs
- Implement a buffer to accumulate data
- Don't wait forever for perfect responses

### Command Freezes

**Challenge**: Commands sometimes appear to hang when waiting for responses.

**Solution**:
- Send command with CR+LF (`\r\n`)
- Short delay after sending (100ms)
- Look for `GNET>` prompt to know command is complete
- Use timeouts to continue even if perfect response not received

### Integration Report

**Challenge**: Determining device IDs and structure.

**Solution**:
- Utilize the integration report from the Lutron app
- Integration report contains:
  - Complete zone listing with IDs and names
  - Area information
  - Device details

## Code Structure

### Minimal Working Example

```python
import socket
import time

class LutronQuick:
    def __init__(self, host, port=23, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            
            # Login sequence
            self._read_with_timeout(b"login: ")
            self._send("lutron")
            self._read_with_timeout(b"password: ")
            self._send("integration")
            self._read_with_timeout(b"GNET> ")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            return False
    
    def _send(self, data):
        if self.socket:
            self.socket.sendall(f"{data}\r\n".encode())
            time.sleep(0.1)  # Short delay
            return True
        return False
    
    def _read_with_timeout(self, target=None, timeout=None):
        if timeout is None:
            timeout = self.timeout
            
        buffer = b""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                buffer += data
                if target and target in buffer:
                    return buffer
            except socket.timeout:
                break
                
        return buffer if buffer else None
    
    def set_light(self, zone_id, level):
        level = max(0.0, min(100.0, level))
        command = f"#OUTPUT,{zone_id},1,{level:.2f}"
        self._send(command)
        response = self._read_with_timeout(b"GNET> ")
        return True
    
    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None
```

## Zone Control Examples

- **Turn light ON**: `#OUTPUT,10,1,100.00`
- **Turn light OFF**: `#OUTPUT,10,1,0.00`
- **Dim to 50%**: `#OUTPUT,10,1,50.00`

## Common Mistakes to Avoid

1. **Infinite Waits**: Never wait indefinitely for a response
2. **No Timeouts**: Always use socket timeouts (3-5 seconds recommended)
3. **Wrong Line Endings**: Always use CR+LF (`\r\n`), never just LF
4. **Not Checking Errors**: Check for `~ERROR` in responses
5. **Not Closing Connection**: Always close the connection when done
6. **Complex Protocols**: The simplest implementation works best

## Verification Steps

1. **Enable Telnet**: Ensure Telnet integration is enabled in the Lutron app
2. **Test Connection**: Verify socket connection to port 23 works
3. **Test Authentication**: Make sure login/password authentication works
4. **Send Simple Command**: Test with a basic command (like turning on/off one light)
5. **Check Response**: Look for error responses from the bridge

## Debugging Tips

1. **Raw Socket Testing**: Use a tool like PuTTY or telnet to manually test the connection
2. **Print Byte Data**: When debugging, print raw byte data (hex format)
3. **Start Simple**: Begin with the simplest commands (ON/OFF) before trying complex ones
4. **Enable Logging**: Log all sent commands and received responses
5. **Check Timeouts**: Verify timeouts are being handled correctly

## References

- Based on [upsert/liplib](https://github.com/upsert/liplib)
- Lutron Integration Protocol Reference

---

*This guide was created based on implementation experience with Lutron Caseta Smart Bridge Pro (May 2025)* 