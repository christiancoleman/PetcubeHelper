"""
Configuration Module for PetCube Helper

This module handles application settings, including loading, saving, and
managing safe zone configuration.
"""

import os
import json

class ConfigManager:
	def __init__(self, logger=None):
		"""Initialize the configuration manager.
		
		Args:
			logger: Function to use for logging messages
		"""
		self.logger = logger or (lambda msg: print(msg))
		self.config_file = 'petcube_settings.json'
		
		# Default settings
		self.settings = {
			'safe_zone_pct': {
				'min_x': 0.3,   # 30% from left
				'max_x': 0.7,   # 70% from left
				'min_y': 0.5,   # 50% from top (bottom half of screen)
				'max_y': 0.9,   # 90% from top
			},
			'default_pattern': 'Kitty Mode',
			'default_interval': 60,
			'default_intensity': 0.5,
			'default_time_unit_ms': 1000,  # 1 second
		}
		
		# Load saved settings if available
		self.load_settings()
	
	def log(self, message):
		"""Log a message using the provided logger function."""
		self.logger(message)
	
	def load_settings(self):
		"""Load settings from the configuration file.
		
		Returns:
			dict: The loaded settings
		"""
		try:
			if os.path.exists(self.config_file):
				with open(self.config_file, 'r') as f:
					saved_settings = json.load(f)
					
					# Update settings with saved values
					for key, value in saved_settings.items():
						if key in self.settings:
							self.settings[key] = value
							
					self.log(f"Loaded settings from {self.config_file}")
		except Exception as e:
			self.log(f"Error loading settings: {str(e)}")
		
		return self.settings
	
	def save_settings(self):
		"""Save current settings to the configuration file.
		
		Returns:
			bool: True if settings were saved successfully
		"""
		try:
			with open(self.config_file, 'w') as f:
				json.dump(self.settings, f, indent=4)
				
			self.log("Settings saved successfully")
			return True
		except Exception as e:
			self.log(f"Error saving settings: {str(e)}")
			return False
	
	def update_safe_zone(self, min_x, max_x, min_y, max_y):
		"""Update the safe zone settings.
		
		Args:
			min_x: Minimum X percentage (0-1)
			max_x: Maximum X percentage (0-1)
			min_y: Minimum Y percentage (0-1)
			max_y: Maximum Y percentage (0-1)
			
		Returns:
			bool: True if settings were updated successfully
		"""
		# Validate ranges
		if min_x >= max_x:
			self.log("Error: min_x must be less than max_x")
			return False
		if min_y >= max_y:
			self.log("Error: min_y must be less than max_y")
			return False
		if not all(0 <= val <= 1 for val in [min_x, max_x, min_y, max_y]):
			self.log("Error: All values must be between 0 and 1")
			return False
		
		# Update settings
		self.settings['safe_zone_pct'] = {
			'min_x': min_x,
			'max_x': max_x,
			'min_y': min_y,
			'max_y': max_y,
		}
		
		self.log(f"Safe zone updated: X={min_x:.2f}-{max_x:.2f}, Y={min_y:.2f}-{max_y:.2f}")
		return True
	
	def calculate_safe_zone_pixels(self, screen_width, screen_height):
		"""Calculate safe zone in pixels based on screen dimensions.
		
		Args:
			screen_width: Screen width in pixels
			screen_height: Screen height in pixels
			
		Returns:
			dict: Safe zone boundaries in pixels
		"""
		zone_pct = self.settings['safe_zone_pct']
		safe_zone = {
			'min_x': int(screen_width * zone_pct['min_x']),
			'max_x': int(screen_width * zone_pct['max_x']),
			'min_y': int(screen_height * zone_pct['min_y']),
			'max_y': int(screen_height * zone_pct['max_y']),
		}
		
		return safe_zone
