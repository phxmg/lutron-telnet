# Lutron Telnet Controller

A lightweight Python library for controlling Lutron Caseta Smart Bridge Pro devices via the Telnet integration protocol.

## Overview

This project provides a simple and reliable way to control Lutron Caseta lighting systems through the Telnet integration protocol available on Lutron Smart Bridge Pro and Ra2 Select devices. The implementation focuses on stability, proper timeout handling, and reliable communication.

## Requirements

- Python 3.6+
- A Lutron Caseta Smart Bridge Pro (L-BDGPRO2-WH) or Ra2 Select Main Repeater
- Telnet integration enabled on your bridge (via the Lutron app)
- Bridge must have a static IP address

## Repository Structure

- `src/` - Core library code
- `examples/` - Example scripts and usage demonstrations
- `docs/` - Documentation and reference materials

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/phxmg/lutron-telnet.git
   cd lutron-telnet
   ```

2. No additional dependencies are required - the library uses only standard Python libraries.

## Quick Start

```python
from src.lutron_quick import LutronQuick

# Create controller instance
controller = LutronQuick("192.168.1.100")  # Replace with your bridge IP

# Connect to the bridge
if controller.connect():
    # Turn on a light (zone ID 10) to 50% brightness
    controller.set_light(10, 50.0)
    
    # Turn off the light
    controller.set_light(10, 0.0)
    
    # Close the connection
    controller.close()
```

## Example: Controlling Master Bedroom Lights

Run the included example script:

```
python examples/master_bedroom_lights.py
```

Be sure to edit the script to use your bridge's IP address.

## Zone IDs and Integration Report

The `docs/integration_report.json` file contains a complete listing of devices, zones, and areas as exported from a Lutron system. You can use this as a reference for the zone IDs for your own devices.

To find your own zone IDs, you'll need to generate an integration report from your Lutron app.

## Documentation

For detailed implementation information, see the [Lutron Integration Guide](docs/LUTRON_INTEGRATION_GUIDE.md), which includes:

- Connection details and authentication
- Command structure and response format
- Implementation challenges and solutions
- Best practices for reliable communication

## License

MIT

## Acknowledgments

Based on experience with several Lutron integration libraries and documentation. 