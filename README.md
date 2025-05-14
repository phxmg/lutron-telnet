# Lutron Telnet Controller

A lightweight Python library for controlling Lutron Caseta Smart Bridge Pro devices via the Telnet integration protocol.

## Overview

This project provides a simple and reliable way to control Lutron Caseta lighting systems through the Telnet integration protocol available on Lutron Smart Bridge Pro and Ra2 Select devices. The implementation focuses on stability, proper timeout handling, and reliable communication.

## Requirements

- Python 3.6+
- A Lutron Caseta Smart Bridge Pro (L-BDGPRO2-WH) or Ra2 Select Main Repeater
- Telnet integration enabled on your bridge (via the Lutron app)
- Bridge must have a static IP address (configured in src/lutron_zones.py)

## Project Structure

- **Core Library**
  - `src/lutron_controller.py` - Advanced controller with batch and sequential operations
  - `src/lutron_quick.py` - Base communication with the Lutron bridge
  - `src/lutron_zones.py` - Zone definitions and utilities

- **Main Command Line Interface**
  - `lutron_cli.py` - Unified CLI for all Lutron operations

- **Scripts**
  - `scripts/bedroom_lights.py` - Control master bedroom lights
  - `scripts/kitchen_pendants.py` - Control kitchen island pendant lights
  - `scripts/kitchen_all.py` - Control all kitchen lights together
  - `scripts/kitchen_show.py` - Standard light show for kitchen
  - `scripts/kitchen_show_optimized.py` - Optimized light show for kitchen
  - `scripts/lutron_monitor.py` - Monitor real-time bridge activity
  - `scripts/list_zones.py` - List available zones from the integration report

- **Documentation**
  - `docs/LUTRON_GUIDE.md` - Detailed protocol information

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/lutron-telnet.git
   cd lutron-telnet
   ```

2. Make the main CLI script executable:
   ```
   chmod +x lutron_cli.py
   ```

3. No additional dependencies are required - the library uses only standard Python libraries.

## Usage

### Using the Unified CLI

The preferred way to control your Lutron system is through the unified CLI:

```bash
# Control a specific zone
./lutron_cli.py zone --zone-id 10 on
./lutron_cli.py zone --zone-id 30 off
./lutron_cli.py zone --zone-id 27 set --level 50

# Control a room
./lutron_cli.py room kitchen on
./lutron_cli.py room bedroom off

# Run a light show
./lutron_cli.py show kitchen-standard
./lutron_cli.py show kitchen-optimized

# Monitor bridge activity
./lutron_cli.py monitor

# List zones
./lutron_cli.py list
```

### Control Modes

The system supports two control modes for multiple lights:

1. **Batch Mode** (default): Controls all lights nearly simultaneously using multi-threading
   - Ideal for turning all lights on/off at once
   - Example: `./lutron_cli.py room kitchen on`

2. **Sequential Mode**: Controls lights one by one with configurable delay
   - Specify with `--mode sequential`
   - Set delay with `--delay X.X` (in seconds)
   - Example: `./lutron_cli.py room kitchen --mode sequential --delay 1.0 on`

## Protocol Details

The Lutron Caseta integration protocol communicates via Telnet:

- **Connection**: Telnet on port 23
- **Authentication**: Username "lutron", password "integration"
- **Commands**: 
  - `#OUTPUT,{zone_id},1,{level}` - Set light level (0-100)
  - `?DEVICE` - Query devices
  - `?AREA` - Query areas

## Tips for Reliability

- The library includes proper timeouts to prevent hanging
- Adds necessary delays between commands to prevent overwhelming the bridge
- Properly handles partial responses with buffering

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Acknowledgments

Based on practical experience with several Lutron integration libraries and documentation. 