# PetCube Helper

This application automates interactions with the PetCube app using ADB (Android Debug Bridge) to simulate user interactions at regular intervals.

## Features

- Easy-to-use graphical user interface
- Automatically starts the ADB server if not running
- Finds and displays all connected devices (local and network)
- Dynamically verifies and uses the correct PetCube package name
- Launches the PetCube app
- Displays device screenshots directly in the application
- Multiple touch pattern options: Random, Circular, and Fixed Points
- Configurable time intervals for pattern repetition

## Application Versions

- **CLI Version**: `petcube_helper.py` - Command-line interface script
- **GUI Version**: `petcube_helper_gui.py` - Graphical user interface application

## Prerequisites

- Python 3.6+ installed
- ADB (Android Debug Bridge) installed and available in your PATH
- Required Python packages:
  - PIL/Pillow (for the GUI version)
  - tkinter (usually comes with Python)
- A device running the PetCube app with USB debugging enabled

## Installation

1. Clone or download this repository to your local machine
2. Ensure Python 3.6+ is installed
3. Install required packages:
   ```
   pip install pillow
   ```
4. Ensure ADB is installed and in your system PATH

## Usage

### GUI Version (Recommended)

Run the GUI application:

```
python petcube_helper_gui.py
```

The GUI application provides an intuitive interface with:
- Buttons for each major function
- Real-time logging in a scrollable view
- Device screenshot display
- Touch pattern selection and configuration
- Status updates at the bottom of the window

### CLI Version

Run the command-line script:

```
python petcube_helper.py
```

## Using the GUI Application

1. **Start ADB Server**: Click the "Start ADB Server" button to initialize ADB
2. **Find Devices**: Click "Find Devices" to detect connected Android devices
3. **Select a Device**: Choose a device from the dropdown list
4. **Verify Package**: Click "Verify Package" to find the PetCube app
5. **Launch App**: Launch the PetCube application on the device
6. **Configure Pattern**:
   - Select a touch pattern type (Random, Circular, Fixed Points)
   - Set the interval in seconds between pattern repetitions
7. **Start/Stop**: Click "Start Pattern" to begin and "Stop Pattern" to end the automation

### Touch Pattern Types

1. **Random**: Performs 3-7 random taps across the screen
2. **Circular**: Draws a circular pattern of taps around the center of the screen
3. **Fixed Points**: Taps a predefined set of screen coordinates (customizable in the code)

## Screenshots

The application automatically captures and displays screenshots from the device after each major operation, helping you visualize the current state of the app.

## Customization

### Fixed Pattern Coordinates

To customize the Fixed Points pattern, edit the `execute_fixed_pattern()` method in the GUI script:

```python
fixed_points = [
    (200, 500),  # Customize X,Y coordinates
    (500, 800),  # for your specific device
    (800, 500),  # and app layout
    (500, 300),
]
```

## Troubleshooting

- **ADB Not Found**: Ensure Android SDK Platform Tools is installed and in your system PATH
- **No Devices Found**: Check that USB debugging is enabled on your device
- **Connection Failures**: For network devices, verify the IP and port are correct
- **App Launch Failures**: 
  - The package name detection should help identify the correct package
  - Check if the app is installed on the device
- **GUI Issues**:
  - If the screenshots don't display, ensure Pillow is installed correctly
  - If the GUI doesn't start, ensure tkinter is available with your Python installation

## Development

This project uses:
- Tkinter for the GUI
- Threading for non-blocking operations
- PIL/Pillow for image handling
- Subprocess for ADB command execution
