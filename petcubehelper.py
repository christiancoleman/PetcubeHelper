"""
PetCube Helper

A cat-friendly application that automates interactions with the PetCube app
using ADB (Android Debug Bridge) to simulate laser pointer movement patterns.

This is the main application file that ties together all components.
"""

import tkinter as tk
import threading
import queue
import time
import sys
import os
import random

# Import modules
from modules.adb_utils import ADBUtility
from modules.config import ConfigManager
from modules.patterns import PatternExecutor
from modules.ui_components import PetCubeHelperUI
from modules.vision.cat_detector import CatDetector

class PetCubeHelper:
	def __init__(self, root):
		"""Initialize the PetCube Helper application.
		
		Args:
			root: The Tkinter root window
		"""
		# Create log queue for thread-safe logging
		self.log_queue = queue.Queue()
		
		# Initialize components
		self.config_manager = ConfigManager(logger=self.log)
		self.adb_utility = ADBUtility(logger=self.log)
		
		# Create callback manager
		self.callbacks = UICallbacks(self)
		
		# Create UI
		self.ui = PetCubeHelperUI(root, self.callbacks, logger=self.log)
		self.ui.set_log_queue(self.log_queue)
		
		# Initialize pattern executor (without cat detector yet)
		self.pattern_executor = PatternExecutor(self.adb_utility, logger=self.log)
		
		# Cat detection (initialized when enabled)
		self.cat_detector = None
		
		# Set up threading event for stopping operations
		self.stop_event = threading.Event()
		
		# Update UI with loaded settings
		self.update_ui_from_settings()
		
		# Start log polling
		self.poll_log_queue()
		
		# Print welcome message
		self.log("PetCube Helper initialized. Welcome!")
		self.log("Please start by clicking 'Start ADB Server'.")
	
	def log(self, message):
		"""Add a message to the log queue"""
		self.log_queue.put(message)
	
	def poll_log_queue(self):
		"""Poll the log queue and update the log text widget"""
		try:
			while True:
				message = self.log_queue.get_nowait()
				self.ui.update_log(message)
				self.log_queue.task_done()
		except queue.Empty:
			pass
		finally:
			self.ui.root.after(100, self.poll_log_queue)
	
	def update_ui_from_settings(self):
		"""Update UI elements with loaded settings"""
		# Update safe zone settings
		safe_zone_pct = self.config_manager.settings['safe_zone_pct']
		self.ui.update_safe_zone_ui(safe_zone_pct)
		
		# Set default pattern
		if 'default_pattern' in self.config_manager.settings:
			self.ui.pattern_var.set(self.config_manager.settings['default_pattern'])
		
		# Set default interval
		if 'default_interval' in self.config_manager.settings:
			self.ui.interval_var.set(str(self.config_manager.settings['default_interval']))
		
		# Set default intensity
		if 'default_intensity' in self.config_manager.settings:
			self.ui.intensity_var.set(self.config_manager.settings['default_intensity'])
		
		# Set default time unit
		if 'default_time_unit_ms' in self.config_manager.settings:
			self.ui.time_unit_var.set(str(self.config_manager.settings['default_time_unit_ms']))
		
		# Cat detection settings
		if 'cat_detection_enabled' in self.config_manager.settings:
			self.ui.cat_detection_var.set(self.config_manager.settings['cat_detection_enabled'])
			
		# Vision settings
		if 'vision_settings' in self.config_manager.settings:
			vision = self.config_manager.settings['vision_settings']
			if 'detection_interval' in vision:
				self.ui.detection_interval_var.set(str(vision['detection_interval']))
			if 'confidence_threshold' in vision:
				self.ui.confidence_threshold_var.set(str(vision['confidence_threshold']))
			if 'model_type' in vision:
				self.ui.model_var.set(vision['model_type'])
			if 'model_path' in vision:
				self.ui.model_path_var.set(vision['model_path'])
			if 'sensitivity' in vision:
				self.ui.sensitivity_var.set(vision['sensitivity'])
		
		# Pattern settings
		if 'pattern_config' in self.config_manager.settings:
			pattern = self.config_manager.settings['pattern_config']
			if 'lead_distance' in pattern:
				self.ui.lead_distance_var.set(str(pattern['lead_distance']))
			if 'tease_distance' in pattern:
				self.ui.tease_distance_var.set(str(pattern['tease_distance']))
	
	def start_adb(self):
		"""Start the ADB server"""
		self.ui.set_status("Starting ADB server...")
		success = self.adb_utility.ensure_adb_running()
		
		if success:
			self.ui.set_status("ADB server running.")
			
			# Enable device finding
			self.ui.device_button.config(state=tk.NORMAL)
		else:
			self.ui.set_status("Error: ADB not found.")
	
	def find_devices(self):
		"""Find connected Android devices"""
		self.ui.set_status("Searching for devices...")
		devices = self.adb_utility.find_devices()
		
		if devices:
			self.ui.update_device_list(devices)
			self.ui.set_status(f"Found {len(devices)} device(s).")
		else:
			self.ui.set_status("No devices found.")
	
	def set_device(self, device_id):
		"""Set the active device for ADB commands"""
		self.adb_utility.set_active_device(device_id)
	
	def verify_package(self):
		"""Verify the PetCube package name"""
		self.ui.set_status("Verifying package name...")
		
		# Default package name for PetCube
		default_package = "com.petcube.android"
		verified_package = self.adb_utility.verify_package(default_package, "petcube")
		
		if verified_package:
			self.ui.verified_package = verified_package
			self.ui.set_status(f"Package verified: {verified_package}")
			
			# Enable launch button
			self.ui.enable_launch_button(True)
		else:
			self.ui.set_status("No PetCube package found.")
	
	def launch_app(self):
		"""Launch the PetCube app"""
		if not self.ui.verified_package:
			self.log("Error: Package not verified. Please verify package first.")
			return
		
		self.ui.set_status("Starting PetCube app...")
		success = self.adb_utility.launch_app(self.ui.verified_package)
		
		if success:
			self.ui.set_status("App launched successfully.")
			
			# Get screen dimensions for safe zone calculation
			screen_dims = self.adb_utility.get_screen_dimensions()
			if screen_dims:
				self.screen_width, self.screen_height = screen_dims
				
				# Calculate safe zone in pixels
				safe_zone_pct = self.config_manager.settings['safe_zone_pct']
				safe_zone = self.config_manager.calculate_safe_zone_pixels(*screen_dims)
				
				# Update pattern executor with safe zone
				self.pattern_executor.set_safe_zone(safe_zone)
				
				# Take a screenshot and display it
				screenshot_data = self.adb_utility.get_screenshot_data()
				if screenshot_data:
					self.ui.update_screenshot_from_data(screenshot_data, self.screen_width, self.screen_height, safe_zone)
					
					# Enable pattern controls
					self.ui.enable_pattern_buttons(True, False)
			else:
				self.log("Warning: Could not determine screen dimensions. Using defaults.")
		else:
			self.ui.set_status("App launch failed.")
	
	def update_safe_zone(self):
		"""Update the safe zone based on user input"""
		# Get safe zone settings from UI
		safe_zone_pct = self.ui.get_safe_zone_settings()
		if not safe_zone_pct:
			return
		
		# Update config with new percentages
		success = self.config_manager.update_safe_zone(
			safe_zone_pct['min_x'],
			safe_zone_pct['max_x'],
			safe_zone_pct['min_y'],
			safe_zone_pct['max_y']
		)
		
		if success:
			# Calculate pixel values if we have screen dimensions
			if hasattr(self, 'screen_width') and hasattr(self, 'screen_height'):
				safe_zone = self.config_manager.calculate_safe_zone_pixels(self.screen_width, self.screen_height)
				
				# Update pattern executor
				self.pattern_executor.set_safe_zone(safe_zone)
				
				# Update screenshot if we have one
				if hasattr(self.ui, 'screenshot_path') and self.ui.screenshot_path:
					self.ui.update_screenshot(self.ui.screenshot_path, self.screen_width, self.screen_height, safe_zone)
			
			self.ui.set_status("Safe zone updated.")
		else:
			self.ui.set_status("Failed to update safe zone.")
	
	def toggle_cat_detection(self):
		"""Toggle cat detection on/off"""
		enabled = self.ui.cat_detection_var.get()
		
		if enabled:
			self.start_cat_detection()
		else:
			self.stop_cat_detection()
	
	def start_cat_detection(self):
		"""Start the cat detection system"""
		if self.cat_detector is None:
			# Initialize cat detector
			self.log("Initializing cat detection...")
			self.cat_detector = CatDetector(self.adb_utility, logger=self.log)
			
			# Apply current vision settings
			self.apply_vision_settings()
			
			# Update pattern executor with cat detector
			self.pattern_executor.set_cat_detector(self.cat_detector)
		
		# Start detection
		self.log("Starting cat detection...")
		self.cat_detector.start_detection()
		self.ui.set_status("Cat detection active")
		
		# Schedule periodic updates of detection visualization
		self.schedule_detection_updates()
	
	def stop_cat_detection(self):
		"""Stop the cat detection system"""
		if self.cat_detector:
			self.log("Stopping cat detection...")
			self.cat_detector.stop_detection()
			self.ui.set_status("Cat detection stopped")
	
	def schedule_detection_updates(self, interval=1000):
		"""Schedule periodic updates of the detection visualization.
		
		Args:
			interval: Update interval in milliseconds
		"""
		if self.cat_detector and self.ui.cat_detection_var.get():
			# Only update if detection is active
			self.update_detection_visualization()
			
			# Schedule next update
			self.ui.root.after(interval, self.schedule_detection_updates, interval)
	
	def update_detection_visualization(self):
		"""Update the detection visualization with current detection"""
		if not self.cat_detector:
			return
		
		# Save a debug frame with detection visualization
		if self.cat_detector.save_debug_frame():
			# Get the latest debug image
			temp_dir = os.path.join(os.path.dirname(__file__), "temp")
			debug_files = sorted([f for f in os.listdir(temp_dir) 
								 if f.startswith("cat_detection_") and f.endswith(".png")],
								 reverse=True)
			
			if debug_files:
				latest_debug = os.path.join(temp_dir, debug_files[0])
				self.ui.update_detection_image(latest_debug)
				
				# Limit the number of debug images to keep
				if len(debug_files) > 10:
					for old_file in debug_files[10:]:
						try:
							os.remove(os.path.join(temp_dir, old_file))
						except:
							pass
	
	def capture_detection_frame(self):
		"""Capture a frame for detection visualization"""
		if not self.cat_detector:
			self.log("Cat detection not initialized.")
			return
		
		self.log("Capturing detection frame...")
		if self.cat_detector.save_debug_frame():
			self.update_detection_visualization()
			self.ui.set_status("Detection frame captured")
		else:
			self.ui.set_status("Failed to capture detection frame")
	
	def update_detection_sensitivity(self, value):
		"""Update detection sensitivity.
		
		Args:
			value: New sensitivity value
		"""
		if self.cat_detector:
			try:
				sensitivity = float(value)
				if 0.1 <= sensitivity <= 1.0:
					# Adjust confidence threshold based on sensitivity
					# Higher sensitivity = lower threshold
					confidence_threshold = 1.0 - (sensitivity * 0.5)  # Maps 0.1-1.0 to 0.95-0.5
					self.cat_detector.confidence_threshold = confidence_threshold
					
					# Update UI
					self.ui.confidence_threshold_var.set(f"{confidence_threshold:.2f}")
					self.ui.set_status(f"Detection sensitivity updated: {sensitivity:.2f}")
			except ValueError:
				pass
	
	def apply_vision_settings(self):
		"""Apply vision settings to the cat detector"""
		if not self.cat_detector:
			self.log("Cat detection not initialized.")
			return
		
		# Get vision settings from UI
		vision_settings = self.ui.get_vision_settings()
		if not vision_settings:
			return
		
		# Apply settings
		self.log("Applying vision settings...")
		
		self.cat_detector.detection_interval = vision_settings['detection_interval']
		self.cat_detector.confidence_threshold = vision_settings['confidence_threshold']
		
		# Save to config
		self.config_manager.settings['vision_settings'] = vision_settings
		self.config_manager.save_settings()
		
		self.ui.set_status("Vision settings applied")
	
	def apply_pattern_settings(self):
		"""Apply pattern settings to the cat-reactive patterns"""
		if not self.cat_detector or not self.pattern_executor.cat_reactive_patterns:
			self.log("Cat reactive patterns not initialized.")
			return
		
		# Get pattern settings from UI
		pattern_config = self.ui.get_pattern_config()
		if not pattern_config:
			return
		
		# Apply settings
		self.log("Applying pattern settings...")
		
		# Apply to cat reactive patterns
		patterns = self.pattern_executor.cat_reactive_patterns
		patterns.lead_distance = pattern_config['lead_distance']
		patterns.tease_distance = pattern_config['tease_distance']
		
		# Save to config
		self.config_manager.settings['pattern_config'] = pattern_config
		self.config_manager.save_settings()
		
		self.ui.set_status("Pattern settings applied")
	
	def save_settings(self):
		"""Save current settings to file"""
		# Get current settings from UI
		pattern_settings = self.ui.get_pattern_settings()
		
		# Update config with current settings
		self.config_manager.settings['default_pattern'] = pattern_settings['pattern']
		self.config_manager.settings['default_interval'] = pattern_settings['interval']
		self.config_manager.settings['default_intensity'] = pattern_settings['intensity']
		self.config_manager.settings['cat_detection_enabled'] = pattern_settings['cat_detection_enabled']
		self.config_manager.settings['default_time_unit_ms'] = pattern_settings['time_unit_ms']
		
		# Vision and pattern settings are saved when applied
		
		# Save to file
		if self.config_manager.save_settings():
			self.ui.set_status("Settings saved successfully.")
		else:
			self.ui.set_status("Failed to save settings.")
	
	def capture_screenshot(self):
		"""Capture a new screenshot and update the display."""
		self.ui.set_status("Capturing screenshot...")
		
		screenshot_data = self.adb_utility.get_screenshot_data()
		if screenshot_data and hasattr(self, 'screen_width') and hasattr(self, 'screen_height'):
			safe_zone = self.config_manager.calculate_safe_zone_pixels(
				self.screen_width, self.screen_height
			)
			self.ui.update_screenshot_from_data(screenshot_data, self.screen_width, self.screen_height, safe_zone)
			self.ui.set_status("Screenshot captured.")
		else:
			self.ui.set_status("Failed to capture screenshot.")
	
	def start_pattern(self):
		"""Start the selected pattern in a thread"""
		# Get pattern settings from UI
		pattern_settings = self.ui.get_pattern_settings()
		
		# Check if cat detection is needed but not enabled
		pattern_type = pattern_settings['pattern']
		needs_cat_detection = pattern_type in ["Cat Following", "Cat Teasing", "Cat Enrichment"]
		
		if needs_cat_detection and not pattern_settings['cat_detection_enabled']:
			self.log("Cat detection must be enabled for this pattern.")
			messagebox.showwarning("Cat Detection Required", 
								   f"The '{pattern_type}' pattern requires cat detection to be enabled.")
			return
		
		# Set safe zone enforcement
		self.pattern_executor.enable_safe_zone(pattern_settings['safe_zone_enabled'])
		
		# Set time unit
		self.pattern_executor.set_time_unit(pattern_settings['time_unit_ms'])
		
		# Reset the stop event
		self.stop_event.clear()
		
		# Mark pattern as active to minimize safety movement logging
		self.pattern_executor.start_pattern()
		
		# Update UI buttons
		self.ui.enable_pattern_buttons(False, True)
		
		# Start pattern thread with continuous movement
		threading.Thread(
			target=self.continuous_pattern_loop,
			args=(
				pattern_settings['pattern'],
				pattern_settings['interval'],
				pattern_settings['intensity']
			),
			daemon=True
		).start()
	
	def continuous_pattern_loop(self, main_pattern, pattern_change_interval, intensity):
		"""Execute patterns in a continuous loop, changing patterns at intervals.
		
		Args:
			main_pattern: The primary pattern type selected by the user
			pattern_change_interval: Time in seconds between pattern type changes
			intensity: Pattern intensity (0.1-1.0)
		"""
		self.log(f"Starting continuous movement with primary pattern: {main_pattern}")
		self.log(f"Pattern will change every {pattern_change_interval} seconds")
		self.log(f"Movement intensity: {intensity:.2f}")
		
		self.ui.set_status(f"Running {main_pattern} pattern")
		
		# Initialize movement timer
		self.pattern_executor.update_movement_timer()
		
		# Determine if we're using cat-reactive patterns
		is_cat_reactive = main_pattern in ["Cat Following", "Cat Teasing", "Cat Enrichment"]
		
		# Available patterns for variety (exclude cat-reactive ones if cat detection isn't available)
		if is_cat_reactive and self.cat_detector:
			# We're using cat-reactive patterns, so include all types
			all_patterns = ["Random", "Circular", "Laser Pointer", "Fixed Points", "Kitty Mode", 
						   "Cat Following", "Cat Teasing", "Cat Enrichment"]
		else:
			# Only use non-cat-reactive patterns
			all_patterns = ["Random", "Circular", "Laser Pointer", "Fixed Points", "Kitty Mode"]
		
		# Loop until stop event is set
		next_pattern_change = time.time() + pattern_change_interval
		current_pattern = main_pattern
		running_time = 0
		
		while not self.stop_event.is_set():
			# Time to change patterns?
			current_time = time.time()
			if current_time >= next_pattern_change:
				# Decide on next pattern (usually the main pattern, sometimes a random one)
				if random.random() < 0.7:  # 70% chance to use main pattern
					current_pattern = main_pattern
				else:
					# Choose a different pattern for variety
					other_patterns = [p for p in all_patterns if p != current_pattern]
					current_pattern = random.choice(other_patterns)
				
				self.log(f"Changing to {current_pattern} pattern")
				next_pattern_change = current_time + pattern_change_interval
				
				# Show pattern change in UI
				self.ui.set_status(f"Running {current_pattern} pattern (changes in {pattern_change_interval}s)")
			
			# Calculate sub-pattern length based on intensity
			# Higher intensity = shorter, more varied patterns
			sub_pattern_duration = max(3, 10 * (1.0 - intensity))
			
			# Execute current pattern for a short duration
			self.log(f"Executing {current_pattern} movement sequence")
			self.pattern_executor.execute_pattern(current_pattern, intensity)
			
			# Update status with countdown to next pattern change
			seconds_to_next = max(1, int(next_pattern_change - time.time()))
			self.ui.set_status(f"Running {current_pattern} pattern (changes in {seconds_to_next}s)")
			
			# Very short gap between sub-patterns - just enough for the app to process
			# but short enough that the laser movement appears continuous
			if not self.stop_event.is_set():
				time.sleep(0.1)
			
			running_time += 1
	
	def stop_pattern(self):
		"""Stop the running pattern"""
		self.stop_event.set()
		
		# Mark pattern as inactive to resume normal logging
		self.pattern_executor.stop_pattern()
		
		self.log("Stopping pattern...")
		self.ui.enable_pattern_buttons(True, False)
		self.ui.set_status("Pattern stopped.")


class UICallbacks:
	"""Callback functions for UI events"""
	
	def __init__(self, app):
		"""Initialize with reference to main application.
		
		Args:
			app: The PetCubeHelper application instance
		"""
		self.app = app
	
	def start_adb(self):
		"""Start ADB server button callback"""
		threading.Thread(target=self.app.start_adb, daemon=True).start()
	
	def find_devices(self):
		"""Find devices button callback"""
		threading.Thread(target=self.app.find_devices, daemon=True).start()
	
	def device_selected(self, event):
		"""Device combobox selection callback"""
		# Get selected device from UI
		selected = self.app.ui.device_combo.current()
		if selected >= 0:
			# Get the device ID from the combo value
			device_id = self.app.ui.device_var.get().split(" (")[0]
			threading.Thread(target=self.app.set_device, args=(device_id,), daemon=True).start()
	
	def verify_package(self):
		"""Verify package button callback"""
		threading.Thread(target=self.app.verify_package, daemon=True).start()
	
	def launch_app(self):
		"""Launch app button callback"""
		threading.Thread(target=self.app.launch_app, daemon=True).start()
	
	def update_safe_zone(self):
		"""Update safe zone button callback"""
		threading.Thread(target=self.app.update_safe_zone, daemon=True).start()
	
	def save_settings(self):
		"""Save settings button callback"""
		threading.Thread(target=self.app.save_settings, daemon=True).start()
	
	def toggle_cat_detection(self):
		"""Toggle cat detection checkbox callback"""
		threading.Thread(target=self.app.toggle_cat_detection, daemon=True).start()
	
	def capture_detection_frame(self):
		"""Capture detection frame button callback"""
		threading.Thread(target=self.app.capture_detection_frame, daemon=True).start()
	
	def update_detection_sensitivity(self, value):
		"""Detection sensitivity slider callback"""
		self.app.update_detection_sensitivity(value)
	
	def apply_vision_settings(self):
		"""Apply vision settings button callback"""
		threading.Thread(target=self.app.apply_vision_settings, daemon=True).start()
	
	def apply_pattern_settings(self):
		"""Apply pattern settings button callback"""
		threading.Thread(target=self.app.apply_pattern_settings, daemon=True).start()
	
	def start_pattern(self):
		"""Start pattern button callback"""
		self.app.start_pattern()
	
	def stop_pattern(self):
		"""Stop pattern button callback"""
		self.app.stop_pattern()
	
	def capture_screenshot(self):
		"""Capture screenshot button callback"""
		threading.Thread(target=self.app.capture_screenshot, daemon=True).start()


def main():
	"""Main entry point"""
	# Create the root window
	root = tk.Tk()
	
	# Create the application
	app = PetCubeHelper(root)
	
	# Start the main loop
	root.mainloop()


if __name__ == "__main__":
	main()
