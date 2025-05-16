# PetCube Helper

This script automates interactions with the PetCube app using ADB (Android Debug Bridge) to simulate user interactions at regular intervals.

## Features

- Automatically starts the ADB server if not running
- Finds the best available device (preferring local/USB connections over network)
- Dynamically verifies and uses the correct PetCube package name
- Launches the PetCube app
- Takes screenshots to help determine navigation coordinates
- Provides framework for camera navigation and touch pattern automation

## Prerequisites

- Python 3.6+ installed
- ADB (Android Debug Bridge) installed and available in your PATH
  - Usually part of Android SDK Platform Tools
  - Can be downloaded from Android developer website
- A device running the PetCube app with USB debugging enabled
- For emulators, ensure they're configured correctly and running

## Installation

1. Clone or download this repository to your local machine
2. Ensure Python 3.6+ is installed
3. Ensure ADB is installed and in your system PATH
4. Connect your Android device or start your emulator

## Usage

Run the script:

```
python petcube_helper.py
```

### What the Script Does

1. **Startup Phase**
   - Verifies ADB is available in PATH and starts the ADB server if needed
   - Detects all connected Android devices
   - Intelligently selects the best device (local devices preferred over network)
   - Verifies the correct Petcube package name by searching installed packages

2. **App Interaction Phase**
   - Launches the Petcube app using the verified package name
   - Takes screenshots to help with navigation coordinate determination
   - Provides framework for implementing camera navigation and touch patterns

## Device Selection Logic

The script uses a smart device selection algorithm:
- Local/USB devices are preferred over network devices
- If multiple devices are connected, the first local device is selected
- If only network devices are available, the first one is selected
- Detailed device information is displayed to help with troubleshooting

## Package Verification

The script dynamically verifies the Petcube app package:
- Searches for all packages containing "petcube" in the name
- Uses the default package name if found
- Automatically selects and uses alternatives if the default isn't found
- Provides clear feedback about which package is being used

## Customization

### Navigation Coordinates

You'll need to modify the `navigate_to_camera()` function with the correct coordinates for your specific device and app version. The script takes a screenshot to help determine these coordinates.

To test tap locations manually:
```
adb shell input tap X Y
```

To get the coordinates of a tap on some devices:
```
adb shell getevent -l
```

### Adding Touch Patterns

Once navigation is working, the script will be extended to implement:
- Different touch patterns (circular, random, fixed points)
- Configurable time intervals between interactions
- Loop control for repeated interactions

## Troubleshooting

- **ADB Not Found**: Ensure Android SDK Platform Tools is installed and in your system PATH
- **No Devices Found**: Check that USB debugging is enabled on your device
- **Connection Failures**: For network devices, verify the IP and port are correct
- **App Launch Failures**: 
  - The package name detection should help identify the correct package
  - Check if the app is installed on the device
  - Verify the app's permissions
- **Navigation Issues**: 
  - Review the app_home.png screenshot to determine correct coordinates
  - Different device resolutions require different coordinates

## Development Roadmap

1. Basic connection and app launching ✅
2. Package verification and smart device selection ✅
3. Camera navigation (in progress)
4. Touch pattern implementation
5. Interval timing and looping
6. Configuration options and command-line arguments
7. Error recovery mechanisms
