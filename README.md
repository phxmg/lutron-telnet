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

- **Core Library**
  - `src/lutron_quick.py` - Base communication with the Lutron bridge
  - `src/lutron_controller.py` - Advanced controller with batch and sequential operations
  - `src/lutron_zones.py` - Zone definitions and utilities

- **Control Scripts**
  - `bedroom_lights.py` - Control master bedroom lights
  - `kitchen_pendants.py` - Control kitchen island pendant lights
  - `kitchen_all.py` - Control all kitchen lights together
  - `lights.py` - General-purpose script for controlling multiple lights by zone ID
  - `list_zones.py` - List available zones from the integration report

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/phxmg/lutron-telnet.git
   cd lutron-telnet
   ```

2. Make scripts executable:
   ```
   chmod +x *.py
   ```

3. No additional dependencies are required - the library uses only standard Python libraries.

## Usage

### Controlling Specific Fixtures

```bash
# Master Bedroom Bay Window Lights
./bedroom_lights.py on
./bedroom_lights.py off
./bedroom_lights.py half
./bedroom_lights.py set --level 35.5

# Kitchen Island Pendants
./kitchen_pendants.py on
./kitchen_pendants.py off
./kitchen_pendants.py set --level 80
```

### Controlling Multiple Lights Together

```bash
# All Kitchen Lights at once (batch mode)
./kitchen_all.py on
./kitchen_all.py off

# All Kitchen Lights sequentially with 0.5s delay
./kitchen_all.py --mode sequential --delay 0.5 on

# Any combination of lights by zone ID (batch mode)
./lights.py --zones 10 27 30 on

# Any combination of lights sequentially
./lights.py --zones 10 27 30 --mode sequential off
```

### Listing Zones

```bash
# List all zones from integration report
./list_zones.py --report integration_report.json

# List zones matching an area
./list_zones.py --report integration_report.json --area kitchen
```

### Control Modes

The system supports two control modes for multiple lights:

1. **Batch Mode** (default): Controls all lights nearly simultaneously using multi-threading
   - Ideal for turning all lights on/off at once
   - Example: `./kitchen_all.py on`

2. **Sequential Mode**: Controls lights one by one with configurable delay
   - Specify with `--mode sequential`
   - Set delay with `--delay X.X` (in seconds)
   - Example: `./kitchen_all.py --mode sequential --delay 1.0 on`

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