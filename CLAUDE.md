# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Build
- **Standalone executable**: `pyinstaller --onefile --windowed petcubehelper.py`
- **Install dependencies**: `pip install pillow opencv-python numpy`

### Development
- **Run application**: `python petcubehelper.py`
- **No test suite or linting configuration available**

## Architecture Overview

PetCubeHelper is a Python application that automates laser pointer movements in the PetCube app via Android Debug Bridge (ADB). It features computer vision for cat detection and reactive patterns.

### Key Components

1. **Entry Point**: `petcubehelper.py` - Main application orchestrator managing GUI, threading, and component coordination

2. **Module Organization**:
   - `modules/adb_utils.py`: ADB operations (device detection, screen capture, tap simulation)
   - `modules/config.py`: Settings persistence and safe zone management
   - `modules/patterns.py`: Pattern executor with safety features and cat detection integration
   - `modules/ui_components.py`: Tkinter-based GUI management
   - `modules/vision/`: Computer vision components
     - `cat_detector.py`: OpenCV-based cat detection
     - `cat_patterns.py`: Reactive patterns (following, teasing, enrichment)

3. **Pattern System**: 
   - Base class at `patterns/base_pattern.py` defines pattern interface
   - Patterns use time-unit based commands: `move_to()`, `wait()`, `tap()`
   - Each pattern is a separate file inheriting from BasePattern
   - Patterns can be standard (fixed movements) or reactive (respond to cat position)

### Critical Design Patterns

1. **Threading Model**: 
   - Main thread handles GUI
   - Separate threads for pattern execution and cat detection
   - Queue-based communication between threads

2. **Safe Zone System**: 
   - Boundaries stored as percentages (0-100)
   - Applied to all movements to prevent laser going off-screen
   - Can be set via percentage inputs or drag-on-screenshot

3. **Cat Detection Integration**:
   - Runs in separate thread when enabled
   - Updates shared state with cat position
   - Reactive patterns check cat state to adjust movements

4. **Settings Persistence**: 
   - JSON-based configuration saved to `petcube_settings.json`
   - Includes safe zone, pattern preferences, and timing settings