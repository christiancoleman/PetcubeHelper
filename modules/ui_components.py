"""
UI Components Module for PetCube Helper

This module contains UI creation and management functions for the PetCube Helper.
"""

import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk, ImageDraw

class PetCubeHelperUI:
	def __init__(self, root, callback_manager, logger=None):
		"""Initialize the UI components.
		
		Args:
			root: The Tkinter root window
			callback_manager: Object containing callback functions
			logger: Function to use for logging messages
		"""
		self.root = root
		self.callbacks = callback_manager
		self.logger = logger or (lambda msg: print(msg))
		
		# Configure root window
		self.root.title("PetCube Helper")
		self.root.geometry("900x700")
		self.root.minsize(900, 700)
		
		# UI state variables
		self.selected_device = None
		self.verified_package = None
		self.log_queue = None
		self.screenshot_path = None
		self.photo = None
		
		# Screen dimensions and safe zone
		self.screen_width = 1080  # Default
		self.screen_height = 1920  # Default
		self.safe_zone = {
			'min_x': 0,
			'max_x': 1080,
			'min_y': 0,
			'max_y': 960,
		}
		
		# Create UI elements
		self.create_ui()
	
	def log(self, message):
		"""Log a message using the provided logger function."""
		self.logger(message)
	
	def set_log_queue(self, queue):
		"""Set the log queue for thread-safe logging.
		
		Args:
			queue: The queue to use for logging
		"""
		self.log_queue = queue
	
	def create_ui(self):
		"""Create the user interface elements."""
		# Create main frame with padding
		main_frame = ttk.Frame(self.root, padding="10")
		main_frame.pack(fill=tk.BOTH, expand=True)
		
		# Create control panels
		self.create_adb_panel(main_frame)
		self.create_safe_zone_panel(main_frame)
		self.create_pattern_panel(main_frame)
		
		# Create notebook for tabs
		self.create_notebook(main_frame)
		
		# Create status bar
		self.create_status_bar(main_frame)
	
	def create_adb_panel(self, parent):
		"""Create the ADB control panel.
		
		Args:
			parent: The parent widget
		"""
		control_panel = ttk.LabelFrame(parent, text="ADB Controls", padding="5")
		control_panel.pack(fill=tk.X, padx=5, pady=5)
		
		# Add control buttons
		self.adb_button = ttk.Button(control_panel, text="Start ADB Server", 
									  command=self.callbacks.start_adb)
		self.adb_button.grid(row=0, column=0, padx=5, pady=5)
		
		self.device_button = ttk.Button(control_panel, text="Find Devices", 
									  command=self.callbacks.find_devices)
		self.device_button.grid(row=0, column=1, padx=5, pady=5)
		
		ttk.Label(control_panel, text="Device:").grid(row=0, column=2, padx=5, pady=5)
		self.device_var = tk.StringVar()
		self.device_combo = ttk.Combobox(control_panel, textvariable=self.device_var, 
									 state="readonly", width=30)
		self.device_combo.grid(row=0, column=3, padx=5, pady=5)
		self.device_combo.bind("<<ComboboxSelected>>", self.callbacks.device_selected)
		
		self.package_button = ttk.Button(control_panel, text="Verify Package", 
									   command=self.callbacks.verify_package)
		self.package_button.grid(row=1, column=0, padx=5, pady=5)
		
		self.launch_button = ttk.Button(control_panel, text="Launch App", 
									  command=self.callbacks.launch_app, 
									  state=tk.DISABLED)
		self.launch_button.grid(row=1, column=1, padx=5, pady=5)
	
	def create_safe_zone_panel(self, parent):
		"""Create the safe zone configuration panel.
		
		Args:
			parent: The parent widget
		"""
		safe_zone_frame = ttk.LabelFrame(parent, text="Safe Zone Configuration", padding="5")
		safe_zone_frame.pack(fill=tk.X, padx=5, pady=5)
		
		# X range (horizontal)
		ttk.Label(safe_zone_frame, text="Horizontal Range:").grid(row=0, column=0, padx=5, pady=5)
		
		# Min X (left boundary)
		ttk.Label(safe_zone_frame, text="Left %:").grid(row=0, column=1, padx=5, pady=5)
		self.min_x_var = tk.StringVar(value="30")
		min_x_entry = ttk.Entry(safe_zone_frame, textvariable=self.min_x_var, width=5)
		min_x_entry.grid(row=0, column=2, padx=5, pady=5)
		
		# Max X (right boundary)
		ttk.Label(safe_zone_frame, text="Right %:").grid(row=0, column=3, padx=5, pady=5)
		self.max_x_var = tk.StringVar(value="70")
		max_x_entry = ttk.Entry(safe_zone_frame, textvariable=self.max_x_var, width=5)
		max_x_entry.grid(row=0, column=4, padx=5, pady=5)
		
		# Y range (vertical)
		ttk.Label(safe_zone_frame, text="Vertical Range:").grid(row=1, column=0, padx=5, pady=5)
		
		# Min Y (top boundary)
		ttk.Label(safe_zone_frame, text="Top %:").grid(row=1, column=1, padx=5, pady=5)
		self.min_y_var = tk.StringVar(value="50")
		min_y_entry = ttk.Entry(safe_zone_frame, textvariable=self.min_y_var, width=5)
		min_y_entry.grid(row=1, column=2, padx=5, pady=5)
		
		# Max Y (bottom boundary)
		ttk.Label(safe_zone_frame, text="Bottom %:").grid(row=1, column=3, padx=5, pady=5)
		self.max_y_var = tk.StringVar(value="90")
		max_y_entry = ttk.Entry(safe_zone_frame, textvariable=self.max_y_var, width=5)
		max_y_entry.grid(row=1, column=4, padx=5, pady=5)
		
		# Update and Save buttons
		self.update_zone_button = ttk.Button(safe_zone_frame, text="Update Safe Zone", 
											 command=self.callbacks.update_safe_zone)
		self.update_zone_button.grid(row=0, column=5, rowspan=2, padx=10, pady=5)
		
		self.save_settings_button = ttk.Button(safe_zone_frame, text="Save Settings", 
											   command=self.callbacks.save_settings)
		self.save_settings_button.grid(row=0, column=6, rowspan=2, padx=10, pady=5)
		
		# Description label
		ttk.Label(safe_zone_frame, text="Note: 0% is left/top of screen, 100% is right/bottom", 
				  font=("", 8, "italic")).grid(row=2, column=0, columnspan=7, padx=5, pady=2)
	
	def create_pattern_panel(self, parent):
		"""Create the pattern control panel.
		
		Args:
			parent: The parent widget
		"""
		pattern_frame = ttk.LabelFrame(parent, text="Touch Pattern", padding="5")
		pattern_frame.pack(fill=tk.X, padx=5, pady=5)
		
		ttk.Label(pattern_frame, text="Primary Pattern:").grid(row=0, column=0, padx=5, pady=5)
		self.pattern_var = tk.StringVar(value="Kitty Mode")
		pattern_combo = ttk.Combobox(pattern_frame, textvariable=self.pattern_var, 
								   values=["Kitty Mode", "Random", "Circular", "Laser Pointer", "Fixed Points"], 
								   state="readonly", width=15)
		pattern_combo.grid(row=0, column=1, padx=5, pady=5)
		
		ttk.Label(pattern_frame, text="Pattern Change (sec):").grid(row=0, column=2, padx=5, pady=5)
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
		
		self.start_pattern_button = ttk.Button(pattern_frame, text="Start Movement", 
											   command=self.callbacks.start_pattern, 
											   state=tk.DISABLED)
		self.start_pattern_button.grid(row=0, column=4, padx=5, pady=5)
		
		self.stop_pattern_button = ttk.Button(pattern_frame, text="Stop Movement", 
											  command=self.callbacks.stop_pattern, 
											  state=tk.DISABLED)
		self.stop_pattern_button.grid(row=0, column=5, padx=5, pady=5)
		
		# Add help text about the new continuous movement system
		help_text = "The laser will move continuously. 'Pattern Change' controls how often the movement style changes."
		ttk.Label(pattern_frame, text=help_text, 
				 font=("", 8, "italic")).grid(row=2, column=0, columnspan=6, padx=5, pady=2)
	
	def create_notebook(self, parent):
		"""Create the notebook with tabs.
		
		Args:
			parent: The parent widget
		"""
		notebook = ttk.Notebook(parent)
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
	
	def create_status_bar(self, parent):
		"""Create the status bar.
		
		Args:
			parent: The parent widget
		"""
		self.status_var = tk.StringVar(value="Ready.")
		status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
		status_bar.pack(fill=tk.X, padx=5, pady=2)
	
	def update_device_list(self, devices):
		"""Update the device dropdown with the list of devices.
		
		Args:
			devices: List of tuples (device_id, display_name)
		"""
		if not devices:
			return
		
		# Update the device dropdown
		self.device_combo['values'] = [d[1] for d in devices]
		self.device_combo.current(0)  # Select first device
		self.selected_device = devices[0][0]  # Save the actual device ID
		
		# Enable package verification
		self.package_button.config(state=tk.NORMAL)
	
	def enable_launch_button(self, enabled=True):
		"""Enable or disable the launch button.
		
		Args:
			enabled: Boolean indicating whether to enable the button
		"""
		state = tk.NORMAL if enabled else tk.DISABLED
		self.launch_button.config(state=state)
	
	def enable_pattern_buttons(self, start_enabled=True, stop_enabled=False):
		"""Enable or disable the pattern control buttons.
		
		Args:
			start_enabled: Boolean indicating whether to enable the start button
			stop_enabled: Boolean indicating whether to enable the stop button
		"""
		self.start_pattern_button.config(state=tk.NORMAL if start_enabled else tk.DISABLED)
		self.stop_pattern_button.config(state=tk.NORMAL if stop_enabled else tk.DISABLED)
	
	def set_status(self, message):
		"""Update the status bar text.
		
		Args:
			message: The status message to display
		"""
		self.status_var.set(message)
	
	def update_log(self, message):
		"""Add a message to the log text widget.
		
		Args:
			message: The message to add to the log
		"""
		self.log_text.config(state=tk.NORMAL)
		self.log_text.insert(tk.END, message + "\n")
		self.log_text.see(tk.END)
		self.log_text.config(state=tk.DISABLED)
	
	def update_screenshot(self, filename, screen_width, screen_height, safe_zone):
		"""Update the screenshot canvas with the given image file.
		
		Args:
			filename: The filename of the screenshot
			screen_width: The screen width in pixels
			screen_height: The screen height in pixels
			safe_zone: Dictionary with min_x, max_x, min_y, max_y keys
			
		Returns:
			bool: True if screenshot was updated successfully
		"""
		self.screenshot_path = filename
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.safe_zone = safe_zone
		
		if not os.path.exists(filename):
			self.log(f"Screenshot file not found: {filename}")
			return False
		
		try:
			# Clear any existing items
			self.screenshot_canvas.delete("all")
			
			# Open the image with PIL
			img = Image.open(filename)
			
			# Draw safe zone overlay on a copy of the image
			img_with_overlay = img.copy()
			draw = ImageDraw.Draw(img_with_overlay, 'RGBA')  # Ensure RGBA mode for transparency
			
			# Calculate safe zone coordinates for this image
			img_width, img_height = img.size
			zone_min_x = int(img_width * self.safe_zone['min_x'] / self.screen_width)
			zone_max_x = int(img_width * self.safe_zone['max_x'] / self.screen_width)
			zone_min_y = int(img_height * self.safe_zone['min_y'] / self.screen_height)
			zone_max_y = int(img_height * self.safe_zone['max_y'] / self.screen_height)
			
			# Draw semi-transparent red overlay on excluded areas (more opaque now)
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
			
			# More visible overlay color (higher opacity)
			overlay_color = (255, 0, 0, 128)  # Semi-transparent red, more opaque
			for zone in excluded_zones:
				draw.rectangle(zone, fill=overlay_color)
			
			# Draw a bold green border around the safe zone
			border_width = 5  # Thicker border
			
			# Draw multiple rectangles for a more visible border
			for i in range(border_width):
				draw.rectangle(
					[(zone_min_x + i, zone_min_y + i), (zone_max_x - i, zone_max_y - i)],
					outline=(0, 255, 0),  # Bright green
					width=1
				)
			
			# Add text labels for clarity
			font_size = max(12, min(img_width, img_height) // 40)  # Scale font size to image
			
			# Draw "SAFE ZONE" text at the top of the safe zone
			text_color = (0, 255, 0)  # Bright green
			draw.text(
				(zone_min_x + 10, zone_min_y + 10),
				"SAFE ZONE",
				fill=text_color,
				stroke_width=2,
				stroke_fill=(0, 0, 0)  # Black outline for visibility
			)
			
			# Draw "EXCLUDED" on each excluded zone
			draw.text((10, 10), "EXCLUDED AREA", fill=(255, 0, 0), stroke_width=2, stroke_fill=(0, 0, 0))
			draw.text((10, zone_max_y + 10), "EXCLUDED AREA", fill=(255, 0, 0), stroke_width=2, stroke_fill=(0, 0, 0))
			draw.text((10, zone_min_y + 10), "EXCLUDED", fill=(255, 0, 0), stroke_width=2, stroke_fill=(0, 0, 0))
			draw.text((zone_max_x + 10, zone_min_y + 10), "EXCLUDED", fill=(255, 0, 0), stroke_width=2, stroke_fill=(0, 0, 0))
			
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
			
			self.log(f"Updated screenshot from {filename} with enhanced safe zone overlay")
			return True
		except Exception as e:
			self.log(f"Error displaying screenshot: {str(e)}")
			return False
	
	def get_pattern_settings(self):
		"""Get the current pattern settings.
		
		Returns:
			dict: Dictionary with pattern, interval, intensity, and safe_zone_enabled keys
		"""
		try:
			interval = int(self.interval_var.get())
		except ValueError:
			interval = 60
			self.interval_var.set("60")
		
		return {
			'pattern': self.pattern_var.get(),
			'interval': interval,
			'intensity': self.intensity_var.get(),
			'safe_zone_enabled': self.safe_zone_var.get(),
		}
	
	def get_safe_zone_settings(self):
		"""Get the current safe zone settings.
		
		Returns:
			dict: Dictionary with min_x, max_x, min_y, max_y keys (as percentages)
			or None if invalid
		"""
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
			
			return {
				'min_x': min_x_pct,
				'max_x': max_x_pct,
				'min_y': min_y_pct,
				'max_y': max_y_pct,
			}
		except ValueError as e:
			messagebox.showerror("Invalid Input", str(e))
			return None
	
	def update_safe_zone_ui(self, safe_zone_pct):
		"""Update the safe zone UI elements with the given percentages.
		
		Args:
			safe_zone_pct: Dictionary with min_x, max_x, min_y, max_y keys (as percentages)
		"""
		self.min_x_var.set(str(int(safe_zone_pct['min_x'] * 100)))
		self.max_x_var.set(str(int(safe_zone_pct['max_x'] * 100)))
		self.min_y_var.set(str(int(safe_zone_pct['min_y'] * 100)))
		self.max_y_var.set(str(int(safe_zone_pct['max_y'] * 100)))
