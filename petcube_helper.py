import os
import subprocess
import time
import re
import sys

# Default package name for Petcube
PETCUBE_PACKAGE = "com.petcube.android"

def ensure_adb_running():
    """Make sure ADB server is running."""
    print("Ensuring ADB server is running...")
    
    # Check if ADB is in PATH
    try:
        subprocess.run(["adb", "--version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: ADB not found in PATH. Please install Android SDK Platform Tools.")
        sys.exit(1)
    
    # Start ADB server if it's not running
    result = subprocess.run(["adb", "start-server"], capture_output=True, text=True)
    print("ADB server started")
    return True

def get_best_device():
    """Find the best available device to connect to.
    Prefers local/USB devices over network devices.
    """
    print("Looking for connected Android devices...")
    result = subprocess.run(["adb", "devices", "-l"], capture_output=True, text=True)
    
    # Parse the output to get device list
    lines = result.stdout.strip().split('\n')
    if len(lines) <= 1:
        print("No devices found. Make sure your device is connected.")
        return None
        
    # Skip the first line which is the header
    devices = []
    for line in lines[1:]:
        if line.strip():
            # Example line: "emulator-5554 device product:sdk_gphone_x86 model:Android_SDK_built_for_x86 device:generic_x86"
            # or: "127.0.0.1:5555 device"
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == 'device':
                device_id = parts[0]
                is_network = ':' in device_id
                devices.append({
                    'id': device_id,
                    'is_network': is_network,
                    'description': line
                })
    
    if not devices:
        print("No available devices found.")
        return None
        
    # Prefer local/USB devices over network devices
    local_devices = [d for d in devices if not d['is_network']]
    if local_devices:
        selected = local_devices[0]
        print(f"Selected local device: {selected['id']}")
        return selected['id']
    else:
        selected = devices[0]
        print(f"Selected network device: {selected['id']} (no local devices available)")
        return selected['id']

def verify_petcube_package():
    """Verify and get the correct Petcube package name."""
    print("Verifying Petcube package name...")
    
    # Look for packages containing 'petcube'
    result = subprocess.run(
        ["adb", "shell", "pm", "list", "packages", "petcube"],
        capture_output=True,
        text=True
    )
    
    packages = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            # Extract package name from 'package:com.example.app'
            match = re.search(r'package:(.*)', line)
            if match:
                packages.append(match.group(1))
    
    if not packages:
        print("Warning: No Petcube packages found.")
        return PETCUBE_PACKAGE
    
    # If our expected package is in the list, use it
    if PETCUBE_PACKAGE in packages:
        print(f"Verified package: {PETCUBE_PACKAGE}")
        return PETCUBE_PACKAGE
    
    # Otherwise, use the first one found and alert the user
    selected = packages[0]
    print(f"Found alternative Petcube package: {selected}")
    print(f"Using this instead of default: {PETCUBE_PACKAGE}")
    return selected

def start_petcube_app(package_name):
    """Start the PetCube app."""
    print(f"Starting Petcube app with package: {package_name}...")
    
    # Launch the app
    result = subprocess.run(
        ["adb", "shell", "monkey", "-p", package_name, "1"],
        capture_output=True,
        text=True
    )
    
    # Give the app time to load
    print("Waiting for app to load...")
    time.sleep(5)
    
    # Check if app launch was successful
    if "No activities found to run" in result.stdout:
        print(f"Failed to start Petcube app. Invalid package name: {package_name}")
        return False
        
    print("Petcube app launched successfully")
    return True

def navigate_to_camera():
    """Navigate to the camera view within the PetCube app."""
    print("Navigating to camera view...")
    
    # Wait for app UI to stabilize
    time.sleep(2)
    
    # For debugging, take a screenshot to help with determining coordinates
    get_screenshot("app_home.png")
    print(f"Screenshot saved to app_home.png - check this to determine navigation coordinates")
    
    # Example tap (coordinates need to be determined for your specific device)
    # subprocess.run(["adb", "shell", "input", "tap", "500", "500"])
    
    print("Note: You'll need to determine the exact coordinates for camera navigation")
    
    return True

def get_screenshot(filename):
    """Take a screenshot to help with debugging."""
    print(f"Taking screenshot to {filename}...")
    subprocess.run(["adb", "shell", "screencap", "/sdcard/screen.png"], capture_output=True)
    subprocess.run(["adb", "pull", "/sdcard/screen.png", filename], capture_output=True)
    subprocess.run(["adb", "shell", "rm", "/sdcard/screen.png"], capture_output=True)
    print(f"Screenshot saved to {filename}")

def main():
    """Main function to run the script."""
    # Ensure ADB is running
    ensure_adb_running()
    
    # Find the best available device
    device_id = get_best_device()
    if not device_id:
        print("No suitable device found. Exiting.")
        return
    
    # Set the selected device as the active one
    if device_id != "127.0.0.1:5555":  # If not the default
        print(f"Connecting to device: {device_id}")
        subprocess.run(["adb", "-s", device_id, "wait-for-device"], capture_output=True)
    else:
        # For network devices that might need explicit connection
        subprocess.run(["adb", "connect", device_id], capture_output=True)
    
    # Verify the Petcube package name
    actual_package = verify_petcube_package()
    
    # Start Petcube app
    if not start_petcube_app(actual_package):
        print("Failed to start Petcube app.")
        return
    
    # Navigate to camera
    if not navigate_to_camera():
        print("Failed to navigate to camera.")
        return
    
    print("Successfully opened Petcube app and ready for camera navigation.")
    print("Ready to implement screen touch patterns.")

if __name__ == "__main__":
    main()
