# PetCube Helper

A cat-friendly application that automates interactions with the PetCube app using ADB (Android Debug Bridge) to simulate continuous laser pointer movement patterns for cat enrichment. Now featuring advanced cat detection that allows the laser to respond to your cat's position and movements!

## Features

### Core Features
- Easy-to-use graphical user interface
- Automatically starts the ADB server if not running
- Finds and displays all connected devices (prioritizes local over network)
- Dynamically verifies and uses the correct PetCube package name
- Launches the PetCube app
- Real-time screenshot display without saving files to disk
- Capture new screenshots on demand

### Time-Based Pattern System (New!)
- **Time Unit Configuration**: Define pattern timing in milliseconds
- **Structured Pattern Commands**: Patterns now use simple commands:
  - Move to position (relative or absolute coordinates)
  - Wait for specified time units
  - Tap (move without wait)
- **Flexible Timing**: Adjust pattern speed by changing the time unit duration
- **Modular Patterns**: Each pattern is in its own file for easy customization

### Cat Detection
- **Computer Vision Integration**: Uses OpenCV to detect your cat in real-time
- **Position Tracking**: Monitors your cat's position and movement patterns
- **Visual Feedback**: Visualizes detection with bounding boxes in the UI
- **Customizable Detection**: Adjust sensitivity and other detection parameters
- **Fallback Patterns**: Automatically reverts to standard patterns when cat is not visible

### Cat-Responsive Patterns
- **Cat Following**: The laser moves just ahead of your cat's predicted path
  - Analyzes movement direction and leads with the right distance
  - Adjusts based on how quickly your cat is moving
- **Cat Teasing**: The laser moves away when your cat approaches
  - Creates engaging "chase me" behavior
  - Maintains optimal distance to keep your cat's interest
- **Cat Enrichment**: Creates patterns around your cat without directly targeting
  - Encourages natural hunting behaviors
  - Creates varied movements in your cat's field of view

### Cat-Optimized Patterns
- **Kitty Mode**: Simulates natural prey movements with multiple behavior types
	- Prey Movement: Small, erratic movements like a mouse
	- Stalking Prey: Slow movement followed by quick darts
	- Hiding Prey: Stop-and-go pattern with brief pauses
	- Fleeing Prey: Quick directional movements
- **Laser Pointer**: Simulates human-controlled laser pointer with natural movements
- **Pattern Types**: Choose from various patterns including Random, Circular, Fixed Points, and cat-reactive patterns

### Safety Features
- **Customizable Safe Zone**: Restrict laser to any portion of the screen
  - Adjustable boundaries using percentage values or by dragging a rectangle on the screenshot
  - Horizontal range: Customizable left and right boundaries
  - Vertical range: Customizable top and bottom boundaries
  - Visual overlay showing safe/restricted areas

### Control Options
- **Time Unit (ms)**: Control the base duration for pattern movements
  - Default: 1000ms (1 second)
  - Minimum: 100ms for very fast patterns
  - Affects all pattern timings proportionally
- **Visual Feedback**: Monitor movements with real-time screenshots and logs
- **Settings Persistence**: Save your safe zone, time unit, and pattern preferences

## Prerequisites

- Python 3.6+ installed
- ADB (Android Debug Bridge) installed and available in your PATH
- Required Python packages:
	- PIL/Pillow (for image processing)
	- OpenCV (for cat detection)
	- tkinter (usually comes with Python)
- A device running the PetCube app with USB debugging enabled

## Installation

1. Clone or download this repository to your local machine
2. Ensure Python 3.6+ is installed
3. Install required packages:
	 ```
	 pip install pillow opencv-python numpy
	 ```
4. Ensure ADB is installed and in your system PATH

## Usage

### Starting the Application

```
python petcubehelper.py
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
2. **Drag on Screenshot**: In the Screenshot tab, click and drag a rectangle to set the safe zone visually
3. **Update Safe Zone**: Click "Update Safe Zone" to apply changes
4. **Save Settings**: Click "Save Settings" to save for future sessions
5. **View Results**: The screenshot will update to show your new safe zone

### Using Screenshots

The application now handles screenshots in memory without saving files:
1. **Auto-capture**: A screenshot is automatically captured when you launch the app
2. **Manual Capture**: Click "Capture Screenshot" in the Screenshot tab to take a new screenshot
3. **Real-time Display**: Screenshots are displayed immediately with safe zone overlay
4. **No File Clutter**: Screenshots are kept in memory, not saved to disk

### Configuring Pattern Timing

1. **Set Time Unit**: Enter the desired time unit duration in milliseconds
   - 1000ms = 1 second (default)
   - 500ms = patterns run at double speed
   - 2000ms = patterns run at half speed
2. **Pattern Commands**: All patterns use time units for their wait commands
3. **Dynamic Adjustment**: Change time unit to speed up or slow down all patterns

### Using Cat Detection

1. **Enable Detection**: Check the "Cat Detection" checkbox in the Touch Pattern panel
2. **View Detection**: Go to the "Cat Detection" tab to see the live detection feed
3. **Adjust Sensitivity**: Use the sensitivity slider to fine-tune detection
   - Higher sensitivity: Detects cats more easily but may have false positives
   - Lower sensitivity: More precise detection but may miss cats in difficult positions
4. **Advanced Settings**: Access the "Settings" tab for more detection options

### Running Patterns

1. **Select Pattern**: Choose from any of the available patterns
   - Standard patterns: Kitty Mode, Laser Pointer, Random, Circular, Fixed Points
   - Cat-reactive patterns: Cat Following, Cat Teasing, Cat Enrichment (requires cat detection)
2. **Configure Time Unit**: Set the base duration for pattern movements
3. **Enable Safe Zone**: Ensure the "Safe Zone" checkbox is selected (recommended)
4. **Start Movement**: Click "Start Movement" to begin laser movement
5. **Stop Movement**: Click "Stop Movement" when finished

## Application Architecture

The application uses a clean, modular architecture with separate components:

```
PetCubeHelper/
├── petcubehelper.py (main application)
├── modules/
│   ├── __init__.py
│   ├── adb_utils.py (ADB operations)
│   ├── config.py (settings management)
│   ├── patterns.py (pattern executor)
│   ├── ui_components.py (UI creation and management)
│   └── vision/
│       ├── __init__.py
│       ├── cat_detector.py (cat detection)
│       └── cat_patterns.py (reactive patterns)
├── patterns/
│   ├── __init__.py
│   ├── base_pattern.py (base class for all patterns)
│   ├── circular_pattern.py
│   ├── random_pattern.py
│   ├── laser_pointer_pattern.py
│   ├── fixed_points_pattern.py
│   └── kitty_mode_pattern.py
├── models/ (detection models)
├── temp/ (temp files for detection)
└── README.md
```

Each module has a specific responsibility:

- **adb_utils.py**: Handles all ADB operations (device detection, app launch, screen taps)
- **config.py**: Manages application settings (loading, saving, safe zone calculation)
- **patterns.py**: Pattern executor that runs pattern files
- **patterns/**: Individual pattern implementations
- **ui_components.py**: Creates and manages the user interface
- **vision/**: Computer vision components for cat detection

## Creating Custom Patterns

With the new pattern system, creating custom patterns is easy:

1. Create a new file in the `patterns/` directory
2. Inherit from `BasePattern` class
3. Implement required methods:
   - `get_name()`: Return the pattern name
   - `get_description()`: Return a description
   - `_setup_commands()`: Define the pattern using commands

Example custom pattern:

```python
from .base_pattern import BasePattern

class MyCustomPattern(BasePattern):
    def get_name(self):
        return "My Custom Pattern"
    
    def get_description(self):
        return "A custom pattern that does something special"
    
    def _setup_commands(self):
        # Move to center
        self.move_to(0.5, 0.5, relative=True)
        self.wait(1)  # Wait 1 time unit
        
        # Move to corner
        self.move_to(0.2, 0.2, relative=True)
        self.wait(0.5)  # Wait half a time unit
        
        # Quick tap at another position
        self.tap(0.8, 0.8, relative=True)
```

4. Add your pattern to `patterns/__init__.py`:
```python
from .my_custom_pattern import MyCustomPattern

PATTERN_CLASSES = {
    # ... existing patterns ...
    "My Custom Pattern": MyCustomPattern,
}
```

## Pattern Command Reference

### move_to(x, y, relative=False)
Move the laser to a specific position.
- `x, y`: Coordinates (0.0-1.0 if relative, pixels if absolute)
- `relative`: If True, coordinates are relative to safe zone

### wait(units)
Wait for a specified number of time units.
- `units`: Number of time units to wait (can be fractional)

### tap(x, y, relative=False)
Same as move_to but named for clarity (instant move without wait).

## Settings Persistence

Your settings are automatically saved to `petcube_settings.json` when you click "Save Settings":
- Safe zone boundaries
- Default pattern selection
- Time unit duration
- Cat detection preferences

## Troubleshooting

### General Issues
- **ADB Not Found**: Ensure Android SDK Platform Tools is installed and in your system PATH
- **No Devices Found**: Check that USB debugging is enabled on your device
- **App Launch Failures**: The package name detection should help identify the correct package
- **Pattern Issues**: If movements seem off-screen, try adjusting your safe zone settings

### Screenshot Issues
- **Black Screenshot**: Make sure the PetCube app is in the foreground
- **No Screenshot**: Check ADB connection and device permissions
- **Capture Button Not Working**: Ensure a device is connected and app is launched

### Cat Detection Issues
- **Detection Not Working**: Make sure OpenCV is properly installed
- **False Detections**: Decrease the detection sensitivity
- **Slow Performance**: Increase the detection interval for better performance

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to improve the application.

### Areas for Contribution
- New pattern implementations
- Improved cat detection models
- UI enhancements
- Performance optimizations
- Additional safety features

## Creating a Binary

To create a standalone executable:

```
pip install pyinstaller
pyinstaller --onefile --windowed petcubehelper.py
```

## License

This project is provided as-is for personal use with PetCube devices. Please use responsibly and ensure your cat's safety at all times.
