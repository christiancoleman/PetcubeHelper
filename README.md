# PetCube Helper

A cat-friendly application that automates interactions with the PetCube app using ADB (Android Debug Bridge) to simulate continuous laser pointer movement patterns for cat enrichment.

## Features

### Core Features
- Easy-to-use graphical user interface
- Automatically starts the ADB server if not running
- Finds and displays all connected devices (prioritizes local over network)
- Dynamically verifies and uses the correct PetCube package name
- Launches the PetCube app
- Displays device screenshots with safety zone overlay

### Cat-Optimized Patterns
- **Continuous Movement System**: Keeps the laser moving constantly for optimal cat engagement
- **Kitty Mode**: Simulates natural prey movements with multiple behavior types
	- Prey Movement: Small, erratic movements like a mouse
	- Stalking Prey: Slow movement followed by quick darts
	- Hiding Prey: Stop-and-go pattern with brief pauses
	- Fleeing Prey: Quick directional movements
- **Laser Pointer**: Simulates human-controlled laser pointer with natural movements
- **Pattern Variety**: System automatically alternates between patterns to maintain interest

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
	- Higher intensity = faster movements, more frequent changes
	- Lower intensity = slower, more gentle movements with longer sub-patterns
	- Controls both speed of individual movements and frequency of changes within a pattern
- **Pattern Change Interval**: Control how often the pattern type changes (in seconds)
- **Visual Feedback**: Monitor movements with screenshots and logs
- **Settings Persistence**: Save your safe zone and pattern preferences for future sessions

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
2. **Update Safe Zone**: Click "Update Safe Zone" to apply changes
3. **Save Settings**: Click "Save Settings" to save for future sessions
4. **View Results**: The screenshot will update to show your new safe zone

### Running Patterns

1. **Select Primary Pattern**: Choose from Kitty Mode, Laser Pointer, Random, Circular, or Fixed Points
2. **Set Pattern Change Interval**: Enter the time in seconds between pattern style changes
3. **Adjust Intensity**: Use the slider to control speed and complexity
4. **Enable Safe Zone**: Ensure the "Safe Zone" checkbox is selected (recommended)
5. **Start Movement**: Click "Start Movement" to begin continuous laser movement
6. **Stop Movement**: Click "Stop Movement" when finished

## Continuous Movement System

The application uses a continuous movement system to keep the laser in constant motion:

- **No Pauses**: The laser is constantly moving to prevent it from staying in one spot
- **Pattern Changes**: The system will automatically switch between patterns at the specified interval
- **Primary Pattern**: Your selected pattern will be used most of the time (70%)
- **Pattern Variety**: For extra engagement, other patterns will occasionally be used (30%)
- **Seamless Transitions**: Transitions between patterns are smooth and maintain constant movement
- **Status Updates**: The status bar shows which pattern is currently running and when it will change

This approach ensures the laser is always moving, which is better for your cat's safety and engagement.

## Application Architecture

The application uses a clean, modular architecture with separate components:

```
PetCubeHelper/
├── petcubehelper.py (main application)
├── modules/
│   ├── __init__.py
│   ├── adb_utils.py (ADB operations)
│   ├── config.py (settings management)
│   ├── patterns.py (pattern implementation)
│   └── ui_components.py (UI creation and management)
└── README.md
```

Each module has a specific responsibility:

- **adb_utils.py**: Handles all ADB operations (device detection, app launch, screen taps)
- **config.py**: Manages application settings (loading, saving, safe zone calculation)
- **patterns.py**: Implements all touch patterns (random, circular, laser pointer, kitty mode)
- **ui_components.py**: Creates and manages the user interface
- **petcubehelper.py**: Main application that ties everything together

## Pattern Details

### Kitty Mode (Recommended)
Alternates between different prey movement patterns to keep your cat engaged and trigger natural hunting instincts:

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
- **Random**: Unpredictable movements across the safe zone
- **Circular**: Circular movement pattern around the center of the safe zone
- **Fixed Points**: Moves between predefined points in the safe zone

## Understanding the Safe Zone

The application creates a customizable "safe zone" to avoid shining the laser in your cat's eyes:

- **Percentage-Based**: All boundaries are set as percentages of the screen dimensions
- **Visual Feedback**: The screenshot tab shows:
	- Green border around the safe zone
	- Red overlay on restricted areas
	- Text labels clearly marking "SAFE ZONE" and "EXCLUDED AREA"
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

### Modifying the Application

The modular architecture makes it easy to modify specific aspects of the application:

- **Adding New Patterns**: Add methods to the `PatternExecutor` class in `patterns.py`
- **Customizing the UI**: Modify the `PetCubeHelperUI` class in `ui_components.py`
- **Adding New Settings**: Extend the `ConfigManager` class in `config.py`
- **Improving ADB Interaction**: Enhance the `ADBUtility` class in `adb_utils.py`

### Extending Functionality

To add new features, you might want to:

1. Add a new module in the `modules/` directory
2. Import it in `petcubehelper.py`
3. Integrate it with the existing components

### Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to improve the application.
