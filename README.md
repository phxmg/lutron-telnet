# Lutron Telnet Controller

A lightweight Python library for controlling Lutron Caseta Smart Bridge Pro devices via the Telnet integration protocol.

## Overview

This project provides a simple and reliable way to control Lutron Caseta lighting systems through the Telnet integration protocol available on Lutron Smart Bridge Pro and Ra2 Select devices. The implementation focuses on stability, proper timeout handling, and reliable communication.

## Requirements

- Python 3.6+
- A Lutron Caseta Smart Bridge Pro (L-BDGPRO2-WH) or Ra2 Select Main Repeater
- Telnet integration enabled on your bridge (via the Lutron app)
- Bridge must have a static IP address (default: 192.168.49.91)

## Project Structure

- `src/` - Core library code that handles Lutron bridge communication
- `lutron_control.py` - General CLI utility for controlling any light/zone
- `bedroom_lights.py` - Specific utility for master bedroom lights (zone 10)
- `kitchen_pendants.py` - Specific utility for kitchen island pendant lights (zone 30)
- `list_zones.py` - Utility to list all zones from the integration report

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/phxmg/lutron-telnet.git
   cd lutron-telnet
   ```

2. Make scripts executable:
   ```
   chmod +x lutron_control.py bedroom_lights.py kitchen_pendants.py list_zones.py
   ```

3. No additional dependencies are required - the library uses only standard Python libraries.

## Usage - General Control

Control any zone with the general CLI utility:

```bash
# Turn on zone 5 (IP address is hardcoded, but can be overridden)
./lutron_control.py --zone 5 on

# Turn off zone 5 with custom IP
./lutron_control.py --ip 192.168.1.100 --zone 5 off

# Set zone 5 to 75% brightness
./lutron_control.py --zone 5 set --level 75
```

## Usage - Bedroom Lights

Control master bedroom lights with the dedicated utility (zone 10 hardcoded):

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

## Usage - Kitchen Pendant Lights

Control kitchen island pendant lights with the dedicated utility (zone 30 hardcoded):

```bash
# Turn on kitchen pendant lights
./kitchen_pendants.py on

# Turn off kitchen pendant lights
./kitchen_pendants.py off

# Set kitchen pendant lights to 50% brightness
./kitchen_pendants.py half

# Set kitchen pendant lights to custom brightness
./kitchen_pendants.py set --level 35.5
```

## Zone Discovery

List all zones in your system with the zone listing utility:

```bash
# List all zones
./list_zones.py --report integration_report.json

# List only zones in the kitchen
./list_zones.py --report integration_report.json --area kitchen
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