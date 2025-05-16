import os
import subprocess
import time
import re
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk, ImageDraw
import threading
import queue
import random
import math
import json

class PetCubeHelperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PetCube Helper")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        
        # Default package name for Petcube
        self.PETCUBE_PACKAGE = "com.petcube.android"
        
        # Create a queue for thread-safe logging
        self.log_queue = queue.Queue()
        
        # Selected device
        self.selected_device = None
        self.verified_package = None
        
        # Screen dimensions and safe zone
        self.screen_width = 1080  # Default
        self.screen_height = 1920  # Default
        
        # Default safe zone percentages
        self.safe_zone_pct = {
            'min_x': 0.3,   # 30% from left
            'max_x': 0.7,   # 70% from left
            'min_y': 0.5,   # 50% from top (bottom half of screen)
            'max_y': 0.9,   # 90% from top
        }
        
        # Safe zone boundaries in pixels (will be calculated based on screen dimensions)
        self.safe_zone = {
            'min_x': 0,
            'max_x': 1080,
            'min_y': 0,
            'max_y': 960,
        }
        
        # Movement safety timer
        self.last_movement_time = time.time()
        
        # Load saved settings if they exist
        self.load_settings()
        
        # Create UI elements
        self.create_ui()
        
        # Start log polling
        self.poll_log_queue()
        
        # Set up thread event for stopping operations
        self.stop_event = threading.Event()

    def load_settings(self):
        """Load saved settings from file."""
        try:
            if os.path.exists('petcube_settings.json'):
                with open('petcube_settings.json', 'r') as f:
                    settings = json.load(f)
                    
                    # Load safe zone percentages if available
                    if 'safe_zone_pct' in settings:
                        self.safe_zone_pct = settings['safe_zone_pct']
                        self.log(f"Loaded saved safe zone settings: {self.safe_zone_pct}")
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
    
    def save_settings(self):
        """Save current settings to file."""
        try:
            settings = {
                'safe_zone_pct': self.safe_zone_pct,
            }
            
            with open('petcube_settings.json', 'w') as f:
                json.dump(settings, f)
                
            self.log("Settings saved successfully")
        except Exception as e:
            self.log(f"Error saving settings: {str(e)}")

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
        
        # Safe Zone Configuration
        safe_zone_frame = ttk.LabelFrame(main_frame, text="Safe Zone Configuration", padding="5")
        safe_zone_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # X range (horizontal)
        ttk.Label(safe_zone_frame, text="Horizontal Range:").grid(row=0, column=0, padx=5, pady=5)
        
        # Min X (left boundary)
        ttk.Label(safe_zone_frame, text="Left %:").grid(row=0, column=1, padx=5, pady=5)
        self.min_x_var = tk.StringVar(value=str(int(self.safe_zone_pct['min_x'] * 100)))
        min_x_entry = ttk.Entry(safe_zone_frame, textvariable=self.min_x_var, width=5)
        min_x_entry.grid(row=0, column=2, padx=5, pady=5)
        
        # Max X (right boundary)
        ttk.Label(safe_zone_frame, text="Right %:").grid(row=0, column=3, padx=5, pady=5)
        self.max_x_var = tk.StringVar(value=str(int(self.safe_zone_pct['max_x'] * 100)))
        max_x_entry = ttk.Entry(safe_zone_frame, textvariable=self.max_x_var, width=5)
        max_x_entry.grid(row=0, column=4, padx=5, pady=5)
        
        # Y range (vertical)
        ttk.Label(safe_zone_frame, text="Vertical Range:").grid(row=1, column=0, padx=5, pady=5)
        
        # Min Y (top boundary)
        ttk.Label(safe_zone_frame, text="Top %:").grid(row=1, column=1, padx=5, pady=5)
        self.min_y_var = tk.StringVar(value=str(int(self.safe_zone_pct['min_y'] * 100)))
        min_y_entry = ttk.Entry(safe_zone_frame, textvariable=self.min_y_var, width=5)
        min_y_entry.grid(row=1, column=2, padx=5, pady=5)
        
        # Max Y (bottom boundary)
        ttk.Label(safe_zone_frame, text="Bottom %:").grid(row=1, column=3, padx=5, pady=5)
        self.max_y_var = tk.StringVar(value=str(int(self.safe_zone_pct['max_y'] * 100)))
        max_y_entry = ttk.Entry(safe_zone_frame, textvariable=self.max_y_var, width=5)
        max_y_entry.grid(row=1, column=4, padx=5, pady=5)
        
        # Update and Save buttons
        self.update_zone_button = ttk.Button(safe_zone_frame, text="Update Safe Zone", command=self.update_safe_zone)
        self.update_zone_button.grid(row=0, column=5, rowspan=2, padx=10, pady=5)
        
        self.save_settings_button = ttk.Button(safe_zone_frame, text="Save Settings", command=self.save_settings)
        self.save_settings_button.grid(row=0, column=6, rowspan=2, padx=10, pady=5)
        
        # Description label
        ttk.Label(safe_zone_frame, text="Note: 0% is left/top of screen, 100% is right/bottom", 
                  font=("", 8, "italic")).grid(row=2, column=0, columnspan=7, padx=5, pady=2)
        
        # Touch pattern controls
        pattern_frame = ttk.LabelFrame(main_frame, text="Touch Pattern", padding="5")
        pattern_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pattern_frame, text="Pattern:").grid(row=0, column=0, padx=5, pady=5)
        self.pattern_var = tk.StringVar(value="Kitty Mode")
        pattern_combo = ttk.Combobox(pattern_frame, textvariable=self.pattern_var, 
                                   values=["Kitty Mode", "Random", "Circular", "Laser Pointer", "Fixed Points"], 
                                   state="readonly", width=15)
        pattern_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(pattern_frame, text="Interval (sec):").grid(row=0, column=2, padx=5, pady=5)
        self.interval_var = tk.StringVar(value="60")
        interval_entry = ttk.Entry(pattern_frame, textvariable=self.interval_var, width=5)
        interval_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Pattern Intensity Slider
        ttk.Label(pattern_frame, text="Intensity:").grid(row=1, column=0, padx=5, pady=5)
        self.intensity_var = tk.DoubleVar(value=0.5)  # 0.0 to 1.0
        intensity_slider = ttk.Scale(pattern_frame, from_=0.1, to=1.0, orient="horizontal",
                                    variable=self.intensity_var, length=200)
        intensity_slider.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        
        # Safe Zone Controls
        ttk.Label(pattern_frame, text="Safe Zone:").grid(row=1, column=4, padx=5, pady=5)
        self.safe_zone_var = tk.BooleanVar(value=True)
        safe_zone_check = ttk.Checkbutton(pattern_frame, text="Enabled", variable=self.safe_zone_var)
        safe_zone_check.grid(row=1, column=5, padx=5, pady=5)
        
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

    def update_safe_zone(self):
        """Update the safe zone based on user input."""
        try:
            # Get values from entry fields
            min_x_pct = float(self.min_x_var.get()) / 100
            max_x_pct = float(self.max_x_var.get()) / 100
            min_y_pct = float(self.min_y_var.get()) / 100
            max_y_pct = float(self.max_y_var.get()) / 100
            
            # Validate ranges
            if min_x_pct >= max_x_pct:
                raise ValueError("Left % must be less than Right %")
            if min_y_pct >= max_y_pct:
                raise ValueError("Top % must be less than Bottom %")
            if min_x_pct < 0 or max_x_pct > 1 or min_y_pct < 0 or max_y_pct > 1:
                raise ValueError("Percentages must be between 0 and 100")
            
            # Update safe zone percentages
            self.safe_zone_pct = {
                'min_x': min_x_pct,
                'max_x': max_x_pct,
                'min_y': min_y_pct,
                'max_y': max_y_pct,
            }
            
            # Recalculate safe zone pixels based on screen dimensions
            self.calculate_safe_zone()
            
            # Take a new screenshot to update the display
            if self.selected_device:
                self.get_screenshot("safe_zone_update.png")
                
            self.log(f"Safe zone updated: X={self.safe_zone_pct['min_x']:.2f}-{self.safe_zone_pct['max_x']:.2f}, Y={self.safe_zone_pct['min_y']:.2f}-{self.safe_zone_pct['max_y']:.2f}")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            self.log(f"Safe zone update error: {str(e)}")

    def calculate_safe_zone(self):
        """Calculate safe zone in pixels based on screen dimensions and percentages."""
        self.safe_zone = {
            'min_x': int(self.screen_width * self.safe_zone_pct['min_x']),
            'max_x': int(self.screen_width * self.safe_zone_pct['max_x']),
            'min_y': int(self.screen_height * self.safe_zone_pct['min_y']),
            'max_y': int(self.screen_height * self.safe_zone_pct['max_y']),
        }
        
        self.log(f"Safe zone calculated in pixels: X={self.safe_zone['min_x']}-{self.safe_zone['max_x']}, Y={self.safe_zone['min_y']}-{self.safe_zone['max_y']}")

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
                
                # Draw safe zone overlay on a copy of the image
                img_with_overlay = img.copy()
                draw = ImageDraw.Draw(img_with_overlay)
                
                # Calculate safe zone coordinates for this image
                img_width, img_height = img.size
                zone_min_x = int(img_width * self.safe_zone['min_x'] / self.screen_width)
                zone_max_x = int(img_width * self.safe_zone['max_x'] / self.screen_width)
                zone_min_y = int(img_height * self.safe_zone['min_y'] / self.screen_height)
                zone_max_y = int(img_height * self.safe_zone['max_y'] / self.screen_height)
                
                # Draw semi-transparent red overlay on excluded areas
                excluded_zones = [
                    # Top zone (0 to zone_min_y)
                    [(0, 0), (img_width, zone_min_y)],
                    # Bottom zone (zone_max_y to img_height)
                    [(0, zone_max_y), (img_width, img_height)],
                    # Left zone (0 to zone_min_x)
                    [(0, zone_min_y), (zone_min_x, zone_max_y)],
                    # Right zone (zone_max_x to img_width)
                    [(zone_max_x, zone_min_y), (img_width, zone_max_y)]
                ]
                
                overlay_color = (255, 0, 0, 64)  # Semi-transparent red
                for zone in excluded_zones:
                    draw.rectangle(zone, fill=overlay_color)
                
                # Draw a green border around the safe zone
                draw.rectangle([(zone_min_x, zone_min_y), (zone_max_x, zone_max_y)], 
                              outline=(0, 255, 0), width=3)
                
                # Resize to fit canvas while maintaining aspect ratio
                canvas_width = self.screenshot_canvas.winfo_width()
                canvas_height = self.screenshot_canvas.winfo_height()
                
                # Avoid division by zero
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width = 600
                    canvas_height = 400
                
                ratio = min(canvas_width/img_width, canvas_height/img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                img_with_overlay = img_with_overlay.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert to Tkinter PhotoImage
                self.photo = ImageTk.PhotoImage(img_with_overlay)
                
                # Calculate position to center the image
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                
                # Add image to canvas
                self.screenshot_canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
                
                self.log(f"Updated screenshot from {filename} with safe zone overlay")
            except Exception as e:
                self.log(f"Error displaying screenshot: {str(e)}")
        else:
            self.log(f"Screenshot file not found: {filename}")
    
    def check_movement_safety(self):
        """Check if we need to force movement for safety"""
        current_time = time.time()
        time_since_last_movement = current_time - self.last_movement_time
        
        # If more than 1 second has passed without movement, we need to move
        if time_since_last_movement > 1.0:
            self.log("Safety timer triggered - forcing movement")
            return True
        return False
    
    def update_movement_timer(self):
        """Update the last movement timestamp"""
        self.last_movement_time = time.time()
    
    def get_safe_coordinates(self):
        """Get a random point within the safe zone"""
        # Generate random coordinates within safe zone
        x = random.randint(self.safe_zone['min_x'], self.safe_zone['max_x'])
        y = random.randint(self.safe_zone['min_y'], self.safe_zone['max_y'])
        
        return x, y
        
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
        
        # Get screen dimensions for safe zone calculation
        self.get_screen_dimensions()
        
        # Take a screenshot
        success = self.get_screenshot("app_home.png")
        if success:
            self.log("App is now ready for camera navigation")
            
            # Enable pattern controls
            self.start_pattern_button.config(state=tk.NORMAL)
    
    def get_screen_dimensions(self):
        """Get device screen dimensions and calculate safe zone."""
        if not self.selected_device:
            return
            
        result = subprocess.run(
            ["adb", "-s", self.selected_device, "shell", "wm", "size"],
            capture_output=True,
            text=True
        )
        
        # Parse dimensions (example output: "Physical size: 1080x2340")
        size_match = re.search(r'(\d+)x(\d+)', result.stdout)
        if size_match:
            self.screen_width = int(size_match.group(1))
            self.screen_height = int(size_match.group(2))
            
            # Calculate safe zone bounds based on percentages
            self.calculate_safe_zone()
            
            self.log(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
            self.log(f"Safe zone: X={self.safe_zone['min_x']}-{self.safe_zone['max_x']}, Y={self.safe_zone['min_y']}-{self.safe_zone['max_y']}")
        else:
            self.log("Could not determine screen dimensions. Using defaults.")
    
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
        
        # Get intensity value
        intensity = self.intensity_var.get()  # Between 0.1 and 1.0
        self.log(f"Pattern intensity: {intensity:.2f}")
        
        # Initialize movement timer
        self.update_movement_timer()
        
        # Loop until stop event is set
        iteration = 1
        while not self.stop_event.is_set():
            self.log(f"Executing iteration {iteration}...")
            
            # Execute pattern based on type
            if pattern_type == "Random":
                self.execute_random_pattern(intensity)
            elif pattern_type == "Circular":
                self.execute_circular_pattern(intensity)
            elif pattern_type == "Laser Pointer":
                self.execute_laser_pointer_pattern(intensity)
            elif pattern_type == "Fixed Points":
                self.execute_fixed_pattern(intensity)
            elif pattern_type == "Kitty Mode":
                self.execute_kitty_mode_pattern(intensity)
            
            # Take a screenshot to show result if needed
            # Disabled to save device resources during continuous operation
            # self.get_screenshot(f"pattern_iteration_{iteration}.png")
            
            # Calculate wait time based on interval and intensity
            # Higher intensity = shorter intervals between patterns
            adjusted_interval = max(5, int(interval * (1.1 - intensity)))
            
            # Wait for the next interval or until stopped, checking safety timer
            self.log(f"Waiting {adjusted_interval} seconds for next iteration...")
            
            wait_start = time.time()
            while (time.time() - wait_start) < adjusted_interval:
                if self.stop_event.is_set():
                    break
                    
                # Check if we need to move for safety (no more than 1 second static)
                if self.check_movement_safety():
                    # Make a small safe movement
                    self.make_safety_movement(intensity)
                    # Reset wait timer for next pattern
                    wait_start = time.time()
                
                self.set_status(f"Running {pattern_type} pattern. Next in {adjusted_interval - int(time.time() - wait_start)}s")
                time.sleep(0.2)  # Short sleep to keep UI responsive
                
            iteration += 1
    
    def make_safety_movement(self, intensity):
        """Make a small, safe movement to prevent static pointing."""
        self.log("Making safety movement")
        
        # Get current coordinates
        x, y = self.get_safe_coordinates()
        
        # Make a small tap
        self.execute_tap(x, y)
        
        # Update the movement timer
        self.update_movement_timer()
    
    def execute_tap(self, x, y, log_message=None):
        """Execute a tap with safe zone enforcement."""
        # Apply safe zone if enabled
        if self.safe_zone_var.get():
            # Keep x within horizontal bounds
            x = max(self.safe_zone['min_x'], min(x, self.safe_zone['max_x']))
            # Keep y within vertical bounds
            y = max(self.safe_zone['min_y'], min(y, self.safe_zone['max_y']))
        
        # Log the tap if message provided
        if log_message:
            self.log(f"{log_message}: ({x}, {y})")
        
        # Execute the tap
        subprocess.run(
            ["adb", "-s", self.selected_device, "shell", "input", "tap", str(x), str(y)],
            capture_output=True
        )
        
        # Update the movement timer
        self.update_movement_timer()
    
    def execute_random_pattern(self, intensity):
        """Execute a random touch pattern."""
        self.log("Executing random touch pattern...")
        
        # Number of taps based on intensity
        num_taps = max(3, int(7 * intensity))
        
        for i in range(num_taps):
            # Generate coordinates within safe zone
            x, y = self.get_safe_coordinates()
            
            # Execute the tap
            self.execute_tap(x, y, f"Tap {i+1}/{num_taps}")
            
            # Delay between taps (shorter with higher intensity)
            delay = max(0.2, 1.5 * (1.0 - intensity))
            time.sleep(random.uniform(0.2, delay))
    
    def execute_circular_pattern(self, intensity):
        """Execute a circular touch pattern."""
        self.log("Executing circular touch pattern...")
        
        # Calculate center within safe zone
        center_x = (self.safe_zone['min_x'] + self.safe_zone['max_x']) // 2
        center_y = (self.safe_zone['min_y'] + self.safe_zone['max_y']) // 2
        
        # Calculate radius based on safe zone (smaller of width/height)
        max_radius_x = min(center_x - self.safe_zone['min_x'], self.safe_zone['max_x'] - center_x)
        max_radius_y = min(center_y - self.safe_zone['min_y'], self.safe_zone['max_y'] - center_y)
        radius = min(max_radius_x, max_radius_y) * 0.8  # 80% of max possible
        
        self.log(f"Drawing circle at ({center_x}, {center_y}) with radius {radius:.1f}")
        
        # Number of points based on intensity
        num_points = max(8, int(16 * intensity))
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            
            # Execute the tap
            self.execute_tap(x, y, f"Tap {i+1}/{num_points}")
            
            # Delay between taps (shorter with higher intensity)
            delay = max(0.1, 0.5 * (1.0 - intensity))
            time.sleep(delay)
    
    def execute_laser_pointer_pattern(self, intensity):
        """Execute a laser pointer-like pattern."""
        self.log("Executing laser pointer pattern...")
        
        # Start with a random point in the safe zone
        last_x, last_y = self.get_safe_coordinates()
        
        # Number of movements based on intensity
        num_moves = max(10, int(20 * intensity))
        
        for i in range(num_moves):
            # Occasionally make a quick dart movement
            if random.random() < 0.3:
                # Quick dart - bigger movement
                new_x = random.randint(self.safe_zone['min_x'], self.safe_zone['max_x'])
                new_y = random.randint(self.safe_zone['min_y'], self.safe_zone['max_y'])
                speed = random.uniform(0.1, 0.3)  # Faster for dart movements
            else:
                # Normal movement - smaller, more controlled
                # Move a short distance from the last position
                max_distance = 200 * intensity  # Max distance based on intensity
                
                # Calculate random vector
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(20, max_distance)
                
                # Calculate new position
                new_x = int(last_x + distance * math.cos(angle))
                new_y = int(last_y + distance * math.sin(angle))
                
                speed = random.uniform(0.3, 0.8)  # Slower for normal movements
            
            # Execute the tap
            self.execute_tap(new_x, new_y, f"Laser move {i+1}/{num_moves}")
            
            # Update last position
            last_x, last_y = new_x, new_y
            
            # Delay between movements (varied based on speed)
            delay = speed * (1.0 - intensity)
            time.sleep(max(0.1, delay))
    
    def execute_kitty_mode_pattern(self, intensity):
        """Execute a pattern optimized for cat engagement."""
        self.log("Executing kitty mode pattern...")
        
        # Start at a random position
        last_x, last_y = self.get_safe_coordinates()
        
        # Choose a random pattern type for this iteration
        pattern_type = random.choice([
            "prey_movement",    # Small, erratic movements
            "stalking_prey",    # Slow then quick movements
            "hiding_prey",      # Stop and go
            "fleeing_prey"      # Quick directional movements
        ])
        
        self.log(f"Kitty mode pattern type: {pattern_type}")
        
        if pattern_type == "prey_movement":
            # Small, erratic movements like a mouse
            num_moves = max(15, int(30 * intensity))
            
            for i in range(num_moves):
                # Small random movements
                max_distance = 80 * intensity
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(10, max_distance)
                
                new_x = int(last_x + distance * math.cos(angle))
                new_y = int(last_y + distance * math.sin(angle))
                
                # Execute the tap
                self.execute_tap(new_x, new_y, f"Prey move {i+1}/{num_moves}")
                
                # Update last position
                last_x, last_y = new_x, new_y
                
                # Random short pause
                time.sleep(random.uniform(0.1, 0.3))
                
        elif pattern_type == "stalking_prey":
            # Slow movement followed by quick dart
            num_sequences = max(3, int(6 * intensity))
            
            for seq in range(num_sequences):
                # Slow movements (3-5 steps)
                slow_steps = random.randint(3, 5)
                for i in range(slow_steps):
                    # Very small movements
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(5, 30)
                    
                    new_x = int(last_x + distance * math.cos(angle))
                    new_y = int(last_y + distance * math.sin(angle))
                    
                    # Execute the tap
                    self.execute_tap(new_x, new_y, f"Stalk {seq+1}/{num_sequences} - slow {i+1}/{slow_steps}")
                    
                    # Update last position
                    last_x, last_y = new_x, new_y
                    
                    # Slow movement
                    time.sleep(random.uniform(0.4, 0.7))
                
                # Fast dart
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(100, 200) * intensity
                
                new_x = int(last_x + distance * math.cos(angle))
                new_y = int(last_y + distance * math.sin(angle))
                
                # Execute the tap
                self.execute_tap(new_x, new_y, f"Stalk {seq+1}/{num_sequences} - DART!")
                
                # Update last position
                last_x, last_y = new_x, new_y
                
                # Pause before next sequence
                time.sleep(random.uniform(0.5, 0.9))
                
        elif pattern_type == "hiding_prey":
            # Stop and go pattern
            num_sequences = max(4, int(8 * intensity))
            
            for seq in range(num_sequences):
                # Hold still (but not longer than 1 second)
                freeze_time = random.uniform(0.3, 0.7)
                
                # Log the freeze but don't actually pause longer than safety time
                self.log(f"Hiding {seq+1}/{num_sequences} - freeze for {freeze_time:.1f}s")
                
                # Note: we don't actually freeze for the full time
                # to maintain the safety timer, but we simulate it with tiny movements
                freeze_start = time.time()
                while (time.time() - freeze_start) < freeze_time:
                    # Tiny movement within 2-3 pixels
                    jitter_x = last_x + random.randint(-2, 2)
                    jitter_y = last_y + random.randint(-2, 2)
                    
                    # Execute the tap but don't log to reduce noise
                    self.execute_tap(jitter_x, jitter_y)
                    
                    # Brief pause
                    time.sleep(0.2)
                
                # Quick movement after hiding
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(80, 180) * intensity
                
                new_x = int(last_x + distance * math.cos(angle))
                new_y = int(last_y + distance * math.sin(angle))
                
                # Execute the tap
                self.execute_tap(new_x, new_y, f"Hiding {seq+1}/{num_sequences} - DASH!")
                
                # Update last position
                last_x, last_y = new_x, new_y
                
                # Pause
                time.sleep(random.uniform(0.2, 0.4))
                
        elif pattern_type == "fleeing_prey":
            # Quick directional movements
            # Choose a general direction
            main_angle = random.uniform(0, 2 * math.pi)
            num_moves = max(8, int(15 * intensity))
            
            for i in range(num_moves):
                # Move in generally the same direction with some variation
                angle_variation = random.uniform(-0.5, 0.5)  # Up to 0.5 radians of variation
                move_angle = main_angle + angle_variation
                
                # Distance varies by intensity
                distance = random.uniform(40, 100) * intensity
                
                new_x = int(last_x + distance * math.cos(move_angle))
                new_y = int(last_y + distance * math.sin(move_angle))
                
                # Execute the tap
                self.execute_tap(new_x, new_y, f"Flee {i+1}/{num_moves}")
                
                # Update last position
                last_x, last_y = new_x, new_y
                
                # Quick movement
                time.sleep(random.uniform(0.2, 0.4))
    
    def execute_fixed_pattern(self, intensity):
        """Execute a fixed pattern of touch points."""
        self.log("Executing fixed touch pattern...")
        
        # These coordinates are percentages of the safe zone
        # They will be converted to actual coordinates based on the device's safe zone
        fixed_points_pct = [
            (0.2, 0.3),  # 20% from left, 30% from top of safe zone
            (0.5, 0.7),  # Center horizontal, 70% from top
            (0.8, 0.3),  # 80% from left, 30% from top
            (0.5, 0.2),  # Center horizontal, 20% from top
        ]
        
        # Convert percentages to actual coordinates
        safe_width = self.safe_zone['max_x'] - self.safe_zone['min_x']
        safe_height = self.safe_zone['max_y'] - self.safe_zone['min_y']
        
        fixed_points = [
            (
                int(self.safe_zone['min_x'] + (pct_x * safe_width)),
                int(self.safe_zone['min_y'] + (pct_y * safe_height))
            )
            for pct_x, pct_y in fixed_points_pct
        ]
        
        # Repeat the pattern based on intensity
        repeats = max(1, int(3 * intensity))
        
        for r in range(repeats):
            for i, (x, y) in enumerate(fixed_points):
                # Execute the tap
                self.execute_tap(x, y, f"Fixed tap {r+1}/{repeats} - {i+1}/{len(fixed_points)}")
                
                # Delay between taps (shorter with higher intensity)
                delay = max(0.2, 0.8 * (1.0 - intensity))
                time.sleep(delay)

def main():
    root = tk.Tk()
    app = PetCubeHelperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
