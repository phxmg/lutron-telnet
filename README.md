# Lutron Caseta Telnet Control

A simple Python utility for controlling Lutron Caseta Smart Bridge Pro devices via the Telnet interface.

## Overview

This project provides a simple way to control your Lutron Caseta lights and other devices from the command line using the Telnet integration protocol. It works with the Smart Bridge Pro 2 and uses your existing integration report for device discovery.

## Requirements

- Python 3.6 or later
- Lutron Caseta Smart Bridge Pro (model L-BDGPRO2-WH)
- Telnet integration enabled on your bridge

## Getting Started

1. Make sure you have enabled the Telnet integration on your Smart Bridge Pro:
   - Open the Lutron app on your mobile device
   - Go to Settings → Advanced → Integration
   - Enable Telnet Support

2. Export your integration report from the Lutron app:
   - In the app, go to Settings → Advanced → Integration
   - Select "Email Integration Report"
   - Save the integration report as `integration_report.json` in the same folder as the scripts

3. Make the script executable:
   ```bash
   chmod +x lutron_simple.py
   ```

## Usage

### Listing All Zones

To list all available zones (controllable devices) organized by area:

```bash
python lutron_simple.py list --ip 192.168.49.91 --report integration_report.json
```

### Turning a Zone ON

To turn on a specific zone (e.g., zone ID 5):

```bash
python lutron_simple.py on --ip 192.168.49.91 --zone 5 --report integration_report.json
```

### Turning a Zone OFF

To turn off a specific zone:

```bash
python lutron_simple.py off --ip 192.168.49.91 --zone 5 --report integration_report.json
```

### Setting a Zone to a Specific Level

To set a zone to a specific brightness level (0-100):

```bash
python lutron_simple.py set --ip 192.168.49.91 --zone 5 --level 50 --report integration_report.json
```

## Command Reference

```
usage: lutron_simple.py [-h] --ip IP [--zone ZONE] [--level LEVEL] [--report REPORT] {list,on,off,set}

Control Lutron Caseta devices via Telnet

positional arguments:
  {list,on,off,set}     Command to execute

optional arguments:
  -h, --help            show this help message and exit
  --ip IP, -i IP        IP address of the Lutron bridge
  --zone ZONE, -z ZONE  Zone ID to control
  --level LEVEL, -l LEVEL
                        Level to set (0-100)
  --report REPORT, -r REPORT
                        Path to integration report JSON file
```

## Zone IDs

The zone IDs correspond to the controllable devices in your system. You can find these IDs:
1. By using the `list` command
2. In your integration report under the "Zones" section
3. In the Lutron app's integration report

## Troubleshooting

- If you get connection errors, ensure that Telnet integration is enabled in the Lutron app.
- Verify you're using the correct IP address for your Smart Bridge Pro.
- Make sure your integration report is up to date and properly formatted.

## License

This project is open source. 