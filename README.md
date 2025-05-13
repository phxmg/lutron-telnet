# Lutron Telnet Controller

A lightweight Python library for controlling Lutron Caseta Smart Bridge Pro devices via the Telnet integration protocol.

## Overview

This project provides a simple and reliable way to control Lutron Caseta lighting systems through the Telnet integration protocol available on Lutron Smart Bridge Pro and Ra2 Select devices. The implementation focuses on stability, proper timeout handling, and reliable communication.

## Requirements

- Python 3.6+
- A Lutron Caseta Smart Bridge Pro (L-BDGPRO2-WH) or Ra2 Select Main Repeater
- Telnet integration enabled on your bridge (via the Lutron app)
- Bridge must have a static IP address

## Project Structure

- `src/` - Core library code that handles Lutron bridge communication
- `lutron_control.py` - General CLI utility for controlling any light/zone
- `bedroom_lights.py` - Specific utility for master bedroom lights

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/phxmg/lutron-telnet.git
   cd lutron-telnet
   ```

2. Make scripts executable:
   ```
   chmod +x lutron_control.py
   chmod +x bedroom_lights.py
   ```

3. No additional dependencies are required - the library uses only standard Python libraries.

## Usage - General Control

Control any zone with the general CLI utility:

```bash
# Turn on zone 5
./lutron_control.py --ip 192.168.1.100 --zone 5 on

# Turn off zone 5
./lutron_control.py --ip 192.168.1.100 --zone 5 off

# Set zone 5 to 75% brightness
./lutron_control.py --ip 192.168.1.100 --zone 5 set --level 75
```

## Usage - Bedroom Lights

Control master bedroom lights with the specific utility (zone 10 hardcoded):

```bash
# Turn on bedroom lights
./bedroom_lights.py on

# Turn off bedroom lights
./bedroom_lights.py off

# Set bedroom lights to 50% brightness
./bedroom_lights.py half

# Set bedroom lights to custom brightness
./bedroom_lights.py set --level 35.5
```

## Protocol Details

The Lutron Caseta integration protocol communicates via Telnet:

- **Connection**: Telnet on port 23
- **Authentication**: Username "lutron", password "integration"
- **Commands**: 
  - `#OUTPUT,{zone_id},1,{level}` - Set light level (0-100)
  - `?DEVICE` - Query devices
  - `?AREA` - Query areas

## Tips for Reliability

- Use short timeouts (3-5 seconds) to prevent hanging
- Always use CR+LF line endings
- Accumulate received data in a buffer to handle partial responses

## License

MIT

## Acknowledgments

Based on practical experience with several Lutron integration libraries and documentation. 