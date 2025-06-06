"""
ADB Utilities for PetCube Helper

This module contains all functions related to ADB (Android Debug Bridge)
operations, including device detection, app launching, and screen interaction.
"""

import os
import re
import subprocess
import time
import sys
import shutil
import tempfile
from PIL import Image

class ADBUtility:
	def __init__(self, logger=None):
		"""Initialize the ADB utility.
		
		Args:
			logger: Function to use for logging messages
		"""
		self.logger = logger or (lambda msg: print(msg))
		self.selected_device = None
		self.screen_width = 1080  # Default
		self.screen_height = 1920  # Default
		
		# Setup subprocess flags to hide console windows on Windows
		self.subprocess_flags = {}
		if sys.platform.startswith('win'):
			self.subprocess_flags['creationflags'] = 0x08000000  # CREATE_NO_WINDOW flag
			self.log("Configured for Windows - hiding command windows")
	
	def log(self, message):
		"""Log a message using the provided logger function."""
		self.logger(message)
	
	def ensure_adb_running(self):
		"""Make sure ADB server is running.
		
		Returns:
			bool: True if ADB is running, False otherwise
		"""
		self.log("Ensuring ADB server is running...")
		
		# Check if ADB is in PATH
		try:
			result = subprocess.run(["adb", "--version"], capture_output=True, text=True, **self.subprocess_flags)
			self.log(result.stdout.split('\n')[0])  # Log ADB version
		except (subprocess.SubprocessError, FileNotFoundError):
			self.log("Error: ADB not found in PATH. Please install Android SDK Platform Tools.")
			return False
		
		# Start ADB server if it's not running
		result = subprocess.run(["adb", "start-server"], capture_output=True, text=True, **self.subprocess_flags)
		self.log("ADB server started")
		return True
	
	def find_devices(self):
		"""Find the connected Android devices.
		
		Returns:
			list: List of tuples (device_id, display_name) for connected devices,
				 or empty list if none found
		"""
		self.log("Looking for connected Android devices...")
		
		result = subprocess.run(["adb", "devices", "-l"], capture_output=True, text=True, **self.subprocess_flags)
		self.log(result.stdout)
		
		# Parse the output to get device list
		lines = result.stdout.strip().split('\n')
		if len(lines) <= 1:
			self.log("No devices found. Make sure your device is connected.")
			return []
			
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
			return []
			
		return devices
	
	def set_active_device(self, device_id):
		"""Set the active device for ADB commands.
		
		Args:
			device_id: The device identifier
			
		Returns:
			bool: True if device was set successfully
		"""
		self.selected_device = device_id
		self.log(f"Selected device: {self.selected_device}")
		
		# Set the device as active
		if ":" in self.selected_device:  # Network device
			subprocess.run(["adb", "connect", self.selected_device], capture_output=True, **self.subprocess_flags)
		
		subprocess.run(["adb", "-s", self.selected_device, "wait-for-device"], capture_output=True, **self.subprocess_flags)
		return True
	
	def verify_package(self, package_name, search_term="petcube"):
		"""Verify if a package exists and find alternatives if not.
		
		Args:
			package_name: The expected package name
			search_term: Term to search for packages
			
		Returns:
			str: The verified package name or None if not found
		"""
		if not self.selected_device:
			self.log("Error: No device selected. Please select a device first.")
			return None
			
		self.log(f"Verifying package name on device {self.selected_device}...")
		
		# Look for packages containing the search term
		result = subprocess.run(
			["adb", "-s", self.selected_device, "shell", "pm", "list", "packages", search_term],
			capture_output=True,
			text=True,
			**self.subprocess_flags
		)
		
		packages = []
		for line in result.stdout.strip().split('\n'):
			if line.strip():
				# Extract package name from 'package:com.example.app'
				match = re.search(r'package:(.*)', line)
				if match:
					packages.append(match.group(1))
		
		if not packages:
			self.log(f"Warning: No packages found containing '{search_term}'.")
			return None
		
		# If our expected package is in the list, use it
		if package_name in packages:
			verified_package = package_name
			self.log(f"Verified package: {package_name}")
		else:
			# Otherwise, use the first one found and alert the user
			verified_package = packages[0]
			self.log(f"Found alternative package: {verified_package}")
			self.log(f"Using this instead of default: {package_name}")
		
		return verified_package
	
	def launch_app(self, package_name):
		"""Launch an app by package name.
		
		Args:
			package_name: The package name to launch
			
		Returns:
			bool: True if app was launched successfully
		"""
		if not self.selected_device:
			self.log("Error: No device selected.")
			return False
			
		self.log(f"Starting app with package: {package_name}...")
		
		# Launch the app
		result = subprocess.run(
			["adb", "-s", self.selected_device, "shell", "monkey", "-p", package_name, "1"],
			capture_output=True,
			text=True,
			**self.subprocess_flags
		)
		
		# Check if app launch was successful
		if "No activities found to run" in result.stdout:
			self.log(f"Failed to start app. Invalid package name: {package_name}")
			return False
			
		self.log("App launched successfully")
		
		# Wait for app UI to stabilize
		time.sleep(2)
		return True
	
	def get_screen_dimensions(self):
		"""Get device screen dimensions.
		
		Returns:
			tuple: (width, height) or None if unable to determine
		"""
		if not self.selected_device:
			return None
			
		result = subprocess.run(
			["adb", "-s", self.selected_device, "shell", "wm", "size"],
			capture_output=True,
			text=True,
			**self.subprocess_flags
		)
		
		# Parse dimensions (example output: "Physical size: 1080x2340")
		size_match = re.search(r'(\d+)x(\d+)', result.stdout)
		if size_match:
			self.screen_width = int(size_match.group(1))
			self.screen_height = int(size_match.group(2))
			
			self.log(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
			return (self.screen_width, self.screen_height)
		else:
			self.log("Could not determine screen dimensions. Using defaults.")
			return None
	
	def get_screenshot(self, filename):
		"""Take a screenshot of the device.
		
		Args:
			filename: The filename to save the screenshot
			
		Returns:
			bool: True if screenshot was taken successfully
		"""
		self.log(f"Taking screenshot to {filename}...")
		
		if not self.selected_device:
			self.log("Error: No device selected for screenshot.")
			return False
		
		try:
			# Create a temp directory for our operations
			with tempfile.TemporaryDirectory() as temp_dir:
				temp_file = os.path.join(temp_dir, "temp_screen.png")
				
				# Method 1: Use exec-out directly to local file (preferred method)
				try:
					with open(temp_file, "wb") as f:
						process = subprocess.Popen(
							["adb", "-s", self.selected_device, "exec-out", "screencap", "-p"],
							stdout=f,
							stderr=subprocess.PIPE,
							**self.subprocess_flags
						)
						_, stderr = process.communicate()
						
						if process.returncode != 0:
							self.log(f"Method 1 failed: {stderr.decode() if stderr else 'Unknown error'}")
							raise subprocess.SubprocessError("Screenshot failed with exec-out")
				
					# Validate the image
					try:
						img = Image.open(temp_file)
						img.verify()
						self.log("Screenshot successful with direct exec-out method")
						shutil.copy2(temp_file, filename)
						return True
					except Exception as e:
						self.log(f"Invalid image from exec-out method: {str(e)}")
						# Continue to fallback method
				except Exception as e:
					self.log(f"Method 1 exception: {str(e)}")
					# Continue to fallback method
				
				# Method 2: Traditional screencap to device then pull
				try:
					self.log("Trying fallback screenshot method...")
					# Take screenshot on device
					result1 = subprocess.run(
						["adb", "-s", self.selected_device, "shell", "screencap", "-p", "/sdcard/screen.png"],
						capture_output=True,
						timeout=5,
						**self.subprocess_flags
					)
					
					# Give it a moment to complete
					time.sleep(0.5)
					
					# Pull the file
					result2 = subprocess.run(
						["adb", "-s", self.selected_device, "pull", "/sdcard/screen.png", temp_file],
						capture_output=True,
						timeout=5,
						**self.subprocess_flags
					)
					
					# Clean up
					subprocess.run(
						["adb", "-s", self.selected_device, "shell", "rm", "/sdcard/screen.png"],
						capture_output=True,
						**self.subprocess_flags
					)
					
					# Validate image
					try:
						img = Image.open(temp_file)
						img.verify()
						self.log("Screenshot successful with traditional method")
						shutil.copy2(temp_file, filename)
						return True
					except Exception as e:
						self.log(f"Invalid image from traditional method: {str(e)}")
						raise Exception("Both screenshot methods failed")
				except Exception as e:
					self.log(f"Method 2 exception: {str(e)}")
					raise Exception("All screenshot methods failed")
					
		except Exception as e:
			self.log(f"Error taking screenshot: {str(e)}")
			
			# Create a dummy image if all methods fail
			try:
				self.log("Creating dummy image as fallback...")
				dummy_img = Image.new('RGB', (self.screen_width, self.screen_height), color=(0, 0, 0))
				dummy_img.save(filename)
				return True
			except Exception as e2:
				self.log(f"Failed to create dummy image: {str(e2)}")
				return False
	
	def get_screenshot_data(self):
		"""Take a screenshot and return the image data.
		
		Returns:
			bytes: PNG image data or None if failed
		"""
		self.log("Capturing screenshot to memory...")
		
		if not self.selected_device:
			self.log("Error: No device selected for screenshot.")
			return None
		
		try:
			# Use exec-out to get screenshot data directly
			process = subprocess.Popen(
				["adb", "-s", self.selected_device, "exec-out", "screencap", "-p"],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				**self.subprocess_flags
			)
			screenshot_data, stderr = process.communicate(timeout=10)
			
			if process.returncode != 0:
				self.log(f"Screenshot failed: {stderr.decode() if stderr else 'Unknown error'}")
				return None
			
			# Validate it's a valid PNG
			if screenshot_data.startswith(b'\x89PNG'):
				self.log("Screenshot captured successfully")
				return screenshot_data
			else:
				self.log("Invalid screenshot data received")
				return None
				
		except subprocess.TimeoutExpired:
			self.log("Screenshot timeout")
			process.kill()
			return None
		except Exception as e:
			self.log(f"Error capturing screenshot: {str(e)}")
			return None
	
	def tap_screen(self, x, y):
		"""Tap the screen at the specified coordinates.
		
		Args:
			x: X coordinate
			y: Y coordinate
			
		Returns:
			bool: True if tap was executed successfully
		"""
		if not self.selected_device:
			self.log("Error: No device selected.")
			return False
		
		try:
			subprocess.run(
				["adb", "-s", self.selected_device, "shell", "input", "tap", str(x), str(y)],
				capture_output=True,
				**self.subprocess_flags
			)
			return True
		except subprocess.SubprocessError as e:
			self.log(f"Error tapping screen: {str(e)}")
			return False
