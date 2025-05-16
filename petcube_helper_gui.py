import os
import subprocess
import time
import re
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import threading
import queue

class PetCubeHelperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PetCube Helper")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Default package name for Petcube
        self.PETCUBE_PACKAGE = "com.petcube.android"
        
        # Create a queue for thread-safe logging
        self.log_queue = queue.Queue()
        
        # Selected device
        self.selected_device = None
        self.verified_package = None
        
        # Create UI elements
        self.create_ui()
        
        # Start log polling
        self.poll_log_queue()
        
        # Set up thread event for stopping operations
        self.stop_event = threading.Event()

    def create_ui(self):
        """Create the user interface elements"""
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create top control panel
        control_panel = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        control_panel.pack(fill=tk.X, padx=5, pady=5)
        
        # Add control buttons
        self.adb_button = ttk.Button(control_panel, text="Start ADB Server", command=self.start_adb_thread)
        self.adb_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.device_button = ttk.Button(control_panel, text="Find Devices", command=self.find_devices_thread)
        self.device_button.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(control_panel, text="Device:").grid(row=0, column=2, padx=5, pady=5)
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(control_panel, textvariable=self.device_var, state="readonly", width=30)
        self.device_combo.grid(row=0, column=3, padx=5, pady=5)
        
        self.package_button = ttk.Button(control_panel, text="Verify Package", command=self.verify_package_thread)
        self.package_button.grid(row=1, column=0, padx=5, pady=5)
        
        self.launch_button = ttk.Button(control_panel, text="Launch App", command=self.launch_app_thread, state=tk.DISABLED)
        self.launch_button.grid(row=1, column=1, padx=5, pady=5)
        
        # Touch pattern controls
        pattern_frame = ttk.LabelFrame(main_frame, text="Touch Pattern", padding="5")
        pattern_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pattern_frame, text="Pattern:").grid(row=0, column=0, padx=5, pady=5)
        self.pattern_var = tk.StringVar(value="Random")
        pattern_combo = ttk.Combobox(pattern_frame, textvariable=self.pattern_var, 
                                   values=["Random", "Circular", "Fixed Points"], state="readonly", width=15)
        pattern_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(pattern_frame, text="Interval (sec):").grid(row=0, column=2, padx=5, pady=5)
        self.interval_var = tk.StringVar(value="60")
        interval_entry = ttk.Entry(pattern_frame, textvariable=self.interval_var, width=5)
        interval_entry.grid(row=0, column=3, padx=5, pady=5)
        
        self.start_pattern_button = ttk.Button(pattern_frame, text="Start Pattern", command=self.start_pattern_thread, state=tk.DISABLED)
        self.start_pattern_button.grid(row=0, column=4, padx=5, pady=5)
        
        self.stop_pattern_button = ttk.Button(pattern_frame, text="Stop Pattern", command=self.stop_pattern, state=tk.DISABLED)
        self.stop_pattern_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log tab
        log_frame = ttk.Frame(notebook, padding="5")
        notebook.add(log_frame, text="Log")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Screenshot tab
        screenshot_frame = ttk.Frame(notebook, padding="5")
        notebook.add(screenshot_frame, text="Screenshot")
        
        # Canvas for displaying screenshot
        self.screenshot_canvas = tk.Canvas(screenshot_frame, bg="black")
        self.screenshot_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, padx=5, pady=2)

    def log(self, message):
        """Add a message to the log queue"""
        self.log_queue.put(message)
        
    def poll_log_queue(self):
        """Poll the log queue and update the log text widget"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
                self.log_queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.poll_log_queue)
            
    def set_status(self, message):
        """Update the status bar"""
        self.status_var.set(message)
        
    def update_screenshot(self, filename):
        """Update the screenshot canvas with the given image file"""
        if os.path.exists(filename):
            try:
                # Clear any existing items
                self.screenshot_canvas.delete("all")
                
                # Open the image with PIL
                img = Image.open(filename)
                
                # Resize to fit canvas while maintaining aspect ratio
                canvas_width = self.screenshot_canvas.winfo_width()
                canvas_height = self.screenshot_canvas.winfo_height()
                
                # Avoid division by zero
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width = 600
                    canvas_height = 400
                
                img_width, img_height = img.size
                ratio = min(canvas_width/img_width, canvas_height/img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert to Tkinter PhotoImage
                self.photo = ImageTk.PhotoImage(img)
                
                # Calculate position to center the image
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                
                # Add image to canvas
                self.screenshot_canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
                
                self.log(f"Updated screenshot from {filename}")
            except Exception as e:
                self.log(f"Error displaying screenshot: {str(e)}")
        else:
            self.log(f"Screenshot file not found: {filename}")
    
    # Thread wrappers for long operations
    def start_adb_thread(self):
        threading.Thread(target=self.ensure_adb_running, daemon=True).start()
        
    def find_devices_thread(self):
        threading.Thread(target=self.find_devices, daemon=True).start()
        
    def verify_package_thread(self):
        threading.Thread(target=self.verify_petcube_package, daemon=True).start()
        
    def launch_app_thread(self):
        threading.Thread(target=self.start_petcube_app, daemon=True).start()
        
    def start_pattern_thread(self):
        # Reset the stop event
        self.stop_event.clear()
        threading.Thread(target=self.execute_touch_pattern, daemon=True).start()
    
    def stop_pattern(self):
        """Stop the running pattern"""
        self.stop_event.set()
        self.log("Stopping touch pattern...")
        self.start_pattern_button.config(state=tk.NORMAL)
        self.stop_pattern_button.config(state=tk.DISABLED)
        self.set_status("Pattern stopped.")
            
    # ADB functions
    def ensure_adb_running(self):
        """Make sure ADB server is running."""
        self.log("Ensuring ADB server is running...")
        self.set_status("Starting ADB server...")
        
        # Check if ADB is in PATH
        try:
            result = subprocess.run(["adb", "--version"], capture_output=True, text=True)
            self.log(result.stdout.split('\n')[0])  # Log ADB version
        except (subprocess.SubprocessError, FileNotFoundError):
            self.log("Error: ADB not found in PATH. Please install Android SDK Platform Tools.")
            messagebox.showerror("ADB Not Found", "ADB is not found in the system PATH. Please install Android SDK Platform Tools.")
            self.set_status("Error: ADB not found.")
            return
        
        # Start ADB server if it's not running
        result = subprocess.run(["adb", "start-server"], capture_output=True, text=True)
        self.log("ADB server started")
        self.set_status("ADB server running.")
        
        # Enable device finding
        self.device_button.config(state=tk.NORMAL)
    
    def find_devices(self):
        """Find the connected Android devices."""
        self.log("Looking for connected Android devices...")
        self.set_status("Searching for devices...")
        
        result = subprocess.run(["adb", "devices", "-l"], capture_output=True, text=True)
        self.log(result.stdout)
        
        # Parse the output to get device list
        lines = result.stdout.strip().split('\n')
        if len(lines) <= 1:
            self.log("No devices found. Make sure your device is connected.")
            self.set_status("No devices found.")
            return
            
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
                    display_name = f"{device_id} ({'Network' if is_network else 'Local'})"
                    devices.append((device_id, display_name))
        
        if not devices:
            self.log("No available devices found.")
            self.set_status("No devices available.")
            return
            
        # Update the device dropdown
        self.device_combo['values'] = [d[1] for d in devices]
        self.device_combo.current(0)  # Select first device
        self.selected_device = devices[0][0]  # Save the actual device ID
        
        self.log(f"Selected device: {self.selected_device}")
        self.set_status(f"Found {len(devices)} device(s).")
        
        # Enable package verification
        self.package_button.config(state=tk.NORMAL)
    
    def verify_petcube_package(self):
        """Verify and get the correct Petcube package name."""
        if not self.selected_device:
            self.log("Error: No device selected. Please find and select a device first.")
            messagebox.showwarning("No Device Selected", "Please find and select a device first.")
            return
            
        self.log(f"Verifying Petcube package name on device {self.selected_device}...")
        self.set_status("Verifying package name...")
        
        # Set the device as active
        if ":" in self.selected_device:  # Network device
            subprocess.run(["adb", "connect", self.selected_device], capture_output=True)
        
        subprocess.run(["adb", "-s", self.selected_device, "wait-for-device"], capture_output=True)
        
        # Look for packages containing 'petcube'
        result = subprocess.run(
            ["adb", "-s", self.selected_device, "shell", "pm", "list", "packages", "petcube"],
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
            self.log("Warning: No Petcube packages found on device.")
            messagebox.showwarning("No Petcube Package", "No Petcube packages found on device. Is the app installed?")
            self.set_status("No Petcube package found.")
            return
        
        # If our expected package is in the list, use it
        if self.PETCUBE_PACKAGE in packages:
            self.verified_package = self.PETCUBE_PACKAGE
            self.log(f"Verified package: {self.PETCUBE_PACKAGE}")
        else:
            # Otherwise, use the first one found and alert the user
            self.verified_package = packages[0]
            self.log(f"Found alternative Petcube package: {self.verified_package}")
            self.log(f"Using this instead of default: {self.PETCUBE_PACKAGE}")
        
        self.set_status(f"Package verified: {self.verified_package}")
        
        # Enable the launch button
        self.launch_button.config(state=tk.NORMAL)
    
    def get_screenshot(self, filename):
        """Take a screenshot to help with debugging."""
        self.log(f"Taking screenshot to {filename}...")
        
        if not self.selected_device:
            self.log("Error: No device selected for screenshot.")
            return False
        
        try:
            subprocess.run(["adb", "-s", self.selected_device, "shell", "screencap", "/sdcard/screen.png"], 
                           capture_output=True, check=True)
            subprocess.run(["adb", "-s", self.selected_device, "pull", "/sdcard/screen.png", filename], 
                           capture_output=True, check=True)
            subprocess.run(["adb", "-s", self.selected_device, "shell", "rm", "/sdcard/screen.png"], 
                           capture_output=True)
            
            self.log(f"Screenshot saved to {filename}")
            self.update_screenshot(filename)
            return True
        except subprocess.SubprocessError as e:
            self.log(f"Error taking screenshot: {str(e)}")
            return False
    
    def start_petcube_app(self):
        """Start the PetCube app."""
        if not self.selected_device or not self.verified_package:
            self.log("Error: Device or package not selected. Please verify package first.")
            messagebox.showwarning("Missing Information", "Please select a device and verify the package first.")
            return
            
        self.log(f"Starting Petcube app with package: {self.verified_package}...")
        self.set_status("Starting Petcube app...")
        
        # Launch the app
        result = subprocess.run(
            ["adb", "-s", self.selected_device, "shell", "monkey", "-p", self.verified_package, "1"],
            capture_output=True,
            text=True
        )
        
        # Check if app launch was successful
        if "No activities found to run" in result.stdout:
            self.log(f"Failed to start Petcube app. Invalid package name: {self.verified_package}")
            messagebox.showerror("Launch Failed", f"Failed to start Petcube app with package: {self.verified_package}")
            self.set_status("App launch failed.")
            return
            
        self.log("Petcube app launched successfully")
        self.set_status("App launched successfully.")
        
        # Wait for app UI to stabilize
        time.sleep(2)
        
        # Take a screenshot
        success = self.get_screenshot("app_home.png")
        if success:
            self.log("App is now ready for camera navigation")
            
            # Enable pattern controls
            self.start_pattern_button.config(state=tk.NORMAL)
    
    def execute_touch_pattern(self):
        """Execute the selected touch pattern in a loop."""
        try:
            interval = int(self.interval_var.get())
        except ValueError:
            self.log("Error: Invalid interval. Using default 60 seconds.")
            interval = 60
        
        pattern_type = self.pattern_var.get()
        self.log(f"Starting {pattern_type} touch pattern with {interval}s interval...")
        self.set_status(f"Running {pattern_type} pattern...")
        
        # Disable start and enable stop button
        self.start_pattern_button.config(state=tk.DISABLED)
        self.stop_pattern_button.config(state=tk.NORMAL)
        
        # Loop until stop event is set
        iteration = 1
        while not self.stop_event.is_set():
            self.log(f"Executing iteration {iteration}...")
            
            # Execute pattern based on type
            if pattern_type == "Random":
                self.execute_random_pattern()
            elif pattern_type == "Circular":
                self.execute_circular_pattern()
            elif pattern_type == "Fixed Points":
                self.execute_fixed_pattern()
            
            # Take a screenshot to show result
            self.get_screenshot(f"pattern_iteration_{iteration}.png")
            
            # Wait for the next interval or until stopped
            self.log(f"Waiting {interval} seconds for next iteration...")
            
            for i in range(interval):
                if self.stop_event.is_set():
                    break
                self.set_status(f"Running {pattern_type} pattern. Next in {interval - i}s")
                time.sleep(1)
                
            iteration += 1
    
    def execute_random_pattern(self):
        """Execute a random touch pattern."""
        import random
        
        self.log("Executing random touch pattern...")
        
        # Get device screen dimensions
        result = subprocess.run(
            ["adb", "-s", self.selected_device, "shell", "wm", "size"],
            capture_output=True,
            text=True
        )
        
        # Parse dimensions (example output: "Physical size: 1080x2340")
        size_match = re.search(r'(\d+)x(\d+)', result.stdout)
        if size_match:
            width = int(size_match.group(1))
            height = int(size_match.group(2))
        else:
            # Default size if we can't determine
            width = 1080
            height = 1920
            
        self.log(f"Screen dimensions: {width}x{height}")
        
        # Execute 3-7 random taps
        num_taps = random.randint(3, 7)
        
        for i in range(num_taps):
            # Generate random coordinates within screen bounds
            x = random.randint(int(width * 0.1), int(width * 0.9))
            y = random.randint(int(height * 0.1), int(height * 0.9))
            
            self.log(f"Tap {i+1}/{num_taps}: ({x}, {y})")
            subprocess.run(
                ["adb", "-s", self.selected_device, "shell", "input", "tap", str(x), str(y)],
                capture_output=True
            )
            
            # Slight delay between taps
            time.sleep(random.uniform(0.5, 1.5))
    
    def execute_circular_pattern(self):
        """Execute a circular touch pattern."""
        import math
        
        self.log("Executing circular touch pattern...")
        
        # Get device screen dimensions
        result = subprocess.run(
            ["adb", "-s", self.selected_device, "shell", "wm", "size"],
            capture_output=True,
            text=True
        )
        
        # Parse dimensions (example output: "Physical size: 1080x2340")
        size_match = re.search(r'(\d+)x(\d+)', result.stdout)
        if size_match:
            width = int(size_match.group(1))
            height = int(size_match.group(2))
        else:
            # Default size if we can't determine
            width = 1080
            height = 1920
            
        # Calculate circle center and radius
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 4
        
        self.log(f"Drawing circle at ({center_x}, {center_y}) with radius {radius}")
        
        # Draw circle with 8 points
        num_points = 8
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            
            self.log(f"Tap {i+1}/{num_points}: ({x}, {y})")
            subprocess.run(
                ["adb", "-s", self.selected_device, "shell", "input", "tap", str(x), str(y)],
                capture_output=True
            )
            
            # Slight delay between taps
            time.sleep(0.5)
    
    def execute_fixed_pattern(self):
        """Execute a fixed pattern of touch points."""
        self.log("Executing fixed touch pattern...")
        
        # These coordinates should be customized based on the app's UI
        # For now using placeholder values as a demonstration
        fixed_points = [
            (200, 500),  # Example point 1
            (500, 800),  # Example point 2
            (800, 500),  # Example point 3
            (500, 300),  # Example point 4
        ]
        
        for i, (x, y) in enumerate(fixed_points):
            self.log(f"Tap {i+1}/{len(fixed_points)}: ({x}, {y})")
            subprocess.run(
                ["adb", "-s", self.selected_device, "shell", "input", "tap", str(x), str(y)],
                capture_output=True
            )
            
            # Slight delay between taps
            time.sleep(0.8)

def main():
    root = tk.Tk()
    app = PetCubeHelperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
