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
		
		# Initialize pattern executor
		self.pattern_executor = PatternExecutor(self.adb_utility, logger=self.log)
		
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
				
				# Take a screenshot
				if self.adb_utility.get_screenshot("app_home.png"):
					self.ui.update_screenshot("app_home.png", self.screen_width, self.screen_height, safe_zone)
					
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
	
	def save_settings(self):
		"""Save current settings to file"""
		# Get current settings from UI
		pattern_settings = self.ui.get_pattern_settings()
		
		# Update config with current settings
		self.config_manager.settings['default_pattern'] = pattern_settings['pattern']
		self.config_manager.settings['default_interval'] = pattern_settings['interval']
		self.config_manager.settings['default_intensity'] = pattern_settings['intensity']
		
		# Save to file
		if self.config_manager.save_settings():
			self.ui.set_status("Settings saved successfully.")
		else:
			self.ui.set_status("Failed to save settings.")
	
	def start_pattern(self):
		"""Start the selected pattern in a thread"""
		# Get pattern settings from UI
		pattern_settings = self.ui.get_pattern_settings()
		
		# Set safe zone enforcement
		self.pattern_executor.enable_safe_zone(pattern_settings['safe_zone_enabled'])
		
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
		
		# Available patterns for variety
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
			
			# Periodically take screenshots to show activity (every 30 seconds)
			if running_time % 30 == 0 and not self.stop_event.is_set():
				ss_filename = f"movement_{running_time}s.png"
				self.adb_utility.get_screenshot(ss_filename)
				
				if hasattr(self, 'screen_width') and hasattr(self, 'screen_height'):
					safe_zone = self.config_manager.calculate_safe_zone_pixels(
						self.screen_width, self.screen_height
					)
					self.ui.update_screenshot(ss_filename, self.screen_width, self.screen_height, safe_zone)
	
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
	
	def start_pattern(self):
		"""Start pattern button callback"""
		self.app.start_pattern()
	
	def stop_pattern(self):
		"""Stop pattern button callback"""
		self.app.stop_pattern()


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
