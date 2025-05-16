# PetCube Helper

A cat-friendly application that automates interactions with the PetCube app using ADB (Android Debug Bridge) to simulate laser pointer movement patterns at regular intervals.

## Features

### Core Features
- Easy-to-use graphical user interface
- Automatically starts the ADB server if not running
- Finds and displays all connected devices (prioritizes local over network)
- Dynamically verifies and uses the correct PetCube package name
- Launches the PetCube app
- Displays device screenshots with safety zone overlay

### Cat-Optimized Patterns
- **Kitty Mode**: Simulates natural prey movements with multiple behavior types
  - Prey Movement: Small, erratic movements like a mouse
  - Stalking Prey: Slow movement followed by quick darts
  - Hiding Prey: Stop-and-go pattern with brief pauses
  - Fleeing Prey: Quick directional movements
- **Laser Pointer**: Simulates human-controlled laser pointer with natural movements
- **Random**: Creates unpredictable movement patterns
- **Circular**: Draws circular patterns that trigger chase instincts
- **Fixed Points**: Moves between predefined locations

### Safety Features
- **Customizable Safe Zone**: Restrict laser to any portion of the screen
  - Adjustable boundaries using percentage values
  - Horizontal range: Customizable left and right boundaries
  - Vertical range: Customizable top and bottom boundaries
  - Visual overlay showing safe/restricted areas
- **Continuous Movement**: Prevents laser from staying in one spot
  - Safety timer ensures movement at least every second
  - Prevents accidental eye contact with laser

### Control Options
- **Intensity Slider**: Adjust pattern speed and complexity
  - Higher intensity = faster movements, more variations
  - Lower intensity = slower, more deliberate movements
- **Custom Intervals**: Set time between pattern changes
- **Visual Feedback**: Monitor movements with screenshots and logs
- **Settings Persistence**: Save your safe zone settings for future sessions

## Prerequisites

- Python 3.6+ installed
- ADB (Android Debug Bridge) installed and available in your PATH
- Required Python packages:
  - PIL/Pillow (for image processing)
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

### Starting the Application

Run the GUI application:

```
python petcube_helper_gui.py
```

### Setup Process

1. **Start ADB Server**: Click the "Start ADB Server" button
2. **Find Devices**: Click "Find Devices" to detect connected Android devices
3. **Select a Device**: Choose a device from the dropdown list
4. **Verify Package**: Click "Verify Package" to find the PetCube app
5. **Launch App**: Launch the PetCube application on the device

### Customizing the Safe Zone

1. **Adjust Percentages**: Set your desired boundaries using the percentage fields
   - **Left %**: Left boundary (0% = left edge, 100% = right edge)
   - **Right %**: Right boundary (must be greater than Left %)
   - **Top %**: Top boundary (0% = top edge, 100% = bottom edge)
   - **Bottom %**: Bottom boundary (must be greater than Top %)
2. **Update Safe Zone**: Click "Update Safe Zone" to apply changes
3. **Save Settings**: Click "Save Settings" to save for future sessions
4. **View Results**: The screenshot will update to show your new safe zone

### Running Patterns

1. **Select Pattern Type**: Choose from Kitty Mode, Laser Pointer, Random, Circular, or Fixed Points
2. **Set Interval**: Enter the time in seconds between pattern changes
3. **Adjust Intensity**: Use the slider to control speed and complexity
4. **Enable Safe Zone**: Ensure the "Safe Zone" checkbox is selected (recommended)
5. **Start Pattern**: Click "Start Pattern" to begin
6. **Stop Pattern**: Click "Stop Pattern" when finished

## Pattern Details

### Kitty Mode (Recommended)
This mode intelligently alternates between different prey movement patterns to keep your cat engaged and trigger natural hunting instincts. The pattern types include:

- **Prey Movement**: Small, erratic movements like a mouse or bug
- **Stalking Prey**: Slow movement followed by quick darts
- **Hiding Prey**: Stop-and-go pattern with strategic pauses (but never longer than 1 second)
- **Fleeing Prey**: Quick directional movements in a consistent direction

### Laser Pointer
Simulates a human-controlled laser pointer with:
- Occasional quick darts across the screen
- Natural, fluid movements with varied speed
- Brief pauses followed by movement (never static for more than 1 second)

### Other Patterns
- **Random**: Unpredictable taps across the safe zone
- **Circular**: Circular movement pattern around the center of the safe zone
- **Fixed Points**: Moves between predefined points in the safe zone

## Understanding the Safe Zone

The application creates a customizable "safe zone" to avoid shining the laser in your cat's eyes:

- **Percentage-Based**: All boundaries are set as percentages of the screen dimensions
- **Visual Feedback**: The screenshot tab shows:
  - Green border around the safe zone
  - Red overlay on restricted areas
- **Orientation**: 
  - 0% is the top/left edge of the screen
  - 100% is the bottom/right edge of the screen

For cat-friendly operation, it's usually best to:
- Keep the laser in the lower portion of the screen (set Top % to 50-60)
- Avoid extreme edges where the laser might not be visible
- Adjust based on your specific PetCube camera setup and room layout

## Settings Persistence

Your safe zone settings are automatically saved to `petcube_settings.json` when you click the "Save Settings" button. These settings will be loaded the next time you start the application.

## Troubleshooting

- **ADB Not Found**: Ensure Android SDK Platform Tools is installed and in your system PATH
- **No Devices Found**: Check that USB debugging is enabled on your device
- **App Launch Failures**: 
  - The package name detection should help identify the correct package
  - Check if the app is installed on the device
- **Pattern Issues**:
  - If movements seem off-screen, try adjusting your safe zone settings
  - Adjust the intensity slider to fine-tune the pattern speed
- **Safe Zone Updates**: 
  - Make sure your percentage values are valid (Left < Right, Top < Bottom)
  - All percentages must be between 0 and 100

## For Developers

- The safe zone logic is in `update_safe_zone()`, `calculate_safe_zone()`, and `get_safe_coordinates()`
- Settings persistence is handled by `load_settings()` and `save_settings()`
- The patterns are implemented in methods like `execute_kitty_mode_pattern()` and can be customized
- Movement safety is handled by `check_movement_safety()` and `update_movement_timer()`
