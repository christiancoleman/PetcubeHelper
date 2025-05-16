"""
Patterns Module for PetCube Helper

This module contains all the touch pattern implementations for the PetCube Helper,
including random, circular, laser pointer, and kitty mode patterns.
"""

import random
import math
import time

class PatternExecutor:
	def __init__(self, adb_utility, logger=None):
		"""Initialize the pattern executor.
		
		Args:
			adb_utility: ADBUtility instance for interacting with the device
			logger: Function to use for logging messages
		"""
		self.adb = adb_utility
		self.logger = logger or (lambda msg: print(msg))
		self.last_movement_time = time.time()
		self.safe_zone = {
			'min_x': 0,
			'max_x': 1080,
			'min_y': 0,
			'max_y': 960,
		}
		self.enforce_safe_zone = True
		
		# Pattern execution tracking
		self.pattern_active = False
		self.safety_verbose = False  # Control safety movement logging verbosity
	
	def log(self, message):
		"""Log a message using the provided logger function."""
		self.logger(message)
	
	def set_safe_zone(self, safe_zone):
		"""Set the safe zone boundaries.
		
		Args:
			safe_zone: Dictionary with min_x, max_x, min_y, max_y keys
		"""
		self.safe_zone = safe_zone
	
	def enable_safe_zone(self, enabled=True):
		"""Enable or disable safe zone enforcement.
		
		Args:
			enabled: Boolean indicating whether to enforce the safe zone
		"""
		self.enforce_safe_zone = enabled
	
	def update_movement_timer(self):
		"""Update the last movement timestamp."""
		self.last_movement_time = time.time()
	
	def check_movement_safety(self):
		"""Check if we need to force movement for safety.
		
		Returns:
			bool: True if movement is needed
		"""
		current_time = time.time()
		time_since_last_movement = current_time - self.last_movement_time
		
		# If more than 1 second has passed without movement, we need to move
		if time_since_last_movement > 1.0:
			# Only log safety movement if verbose or not in an active pattern
			if self.safety_verbose or not self.pattern_active:
				self.log("Safety timer triggered - forcing movement")
			return True
		return False
	
	def start_pattern(self):
		"""Mark pattern as active."""
		self.pattern_active = True
	
	def stop_pattern(self):
		"""Mark pattern as inactive."""
		self.pattern_active = False
	
	def execute_tap(self, x, y, log_message=None):
		"""Execute a tap with safe zone enforcement.
		
		Args:
			x: X coordinate
			y: Y coordinate
			log_message: Optional message to log with the tap
			
		Returns:
			bool: True if tap was executed successfully
		"""
		# Apply safe zone if enabled
		if self.enforce_safe_zone:
			# Keep x within horizontal bounds
			orig_x, orig_y = x, y
			x = max(self.safe_zone['min_x'], min(x, self.safe_zone['max_x']))
			y = max(self.safe_zone['min_y'], min(y, self.safe_zone['max_y']))
			
			# Log if coordinates were constrained
			if (x != orig_x or y != orig_y) and log_message and self.safety_verbose:
				self.log(f"Coordinates constrained to safe zone: ({orig_x}, {orig_y}) -> ({x}, {y})")
		
		# Log the tap if message provided
		if log_message:
			self.log(f"{log_message}: ({x}, {y})")
		
		# Execute the tap
		success = self.adb.tap_screen(x, y)
		
		# Update the movement timer
		self.update_movement_timer()
		
		return success
	
	def get_safe_coordinates(self):
		"""Get a random point within the safe zone.
		
		Returns:
			tuple: (x, y) coordinates
		"""
		# Generate random coordinates within safe zone
		x = random.randint(self.safe_zone['min_x'], self.safe_zone['max_x'])
		y = random.randint(self.safe_zone['min_y'], self.safe_zone['max_y'])
		
		return x, y
	
	def make_safety_movement(self, intensity=0.5):
		"""Make a small, safe movement to prevent static pointing.
		
		Args:
			intensity: Movement intensity (0.1-1.0)
		"""
		# Only log if not in an active pattern (reduces log noise)
		if not self.pattern_active or self.safety_verbose:
			self.log("Safety movement to prevent static pointing")
		
		# Get current coordinates
		x, y = self.get_safe_coordinates()
		
		# Make a small tap (without additional logging)
		self.execute_tap(x, y)
	
	def execute_pattern(self, pattern_type, intensity=0.5):
		"""Execute the specified pattern.
		
		Args:
			pattern_type: The pattern type to execute
			intensity: Pattern intensity (0.1-1.0)
			
		Returns:
			bool: True if pattern executed successfully
		"""
		self.log(f"Executing {pattern_type} pattern with intensity {intensity:.2f}...")
		
		# Mark pattern as active to suppress safety logs
		self.start_pattern()
		
		try:
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
			else:
				self.log(f"Unknown pattern type: {pattern_type}")
				self.stop_pattern()  # Mark pattern as inactive
				return False
			
			self.stop_pattern()  # Mark pattern as inactive
			return True
		except Exception as e:
			self.log(f"Error executing pattern: {str(e)}")
			self.stop_pattern()  # Mark pattern as inactive
			return False
	
	def execute_random_pattern(self, intensity):
		"""Execute a random touch pattern.
		
		Args:
			intensity: Pattern intensity (0.1-1.0)
		"""
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
		"""Execute a circular touch pattern.
		
		Args:
			intensity: Pattern intensity (0.1-1.0)
		"""
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
		"""Execute a laser pointer-like pattern.
		
		Args:
			intensity: Pattern intensity (0.1-1.0)
		"""
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
	
	def execute_fixed_pattern(self, intensity):
		"""Execute a fixed pattern of touch points.
		
		Args:
			intensity: Pattern intensity (0.1-1.0)
		"""
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
	
	def execute_kitty_mode_pattern(self, intensity):
		"""Execute a pattern optimized for cat engagement.
		
		Args:
			intensity: Pattern intensity (0.1-1.0)
		"""
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
			self._execute_prey_movement(last_x, last_y, intensity)
				
		elif pattern_type == "stalking_prey":
			# Slow movement followed by quick dart
			self._execute_stalking_prey(last_x, last_y, intensity)
				
		elif pattern_type == "hiding_prey":
			# Stop and go pattern
			self._execute_hiding_prey(last_x, last_y, intensity)
				
		elif pattern_type == "fleeing_prey":
			# Quick directional movements
			self._execute_fleeing_prey(last_x, last_y, intensity)
	
	def _execute_prey_movement(self, start_x, start_y, intensity):
		"""Execute prey movement pattern (small, erratic movements).
		
		Args:
			start_x: Starting X coordinate
			start_y: Starting Y coordinate
			intensity: Pattern intensity (0.1-1.0)
		"""
		# Small, erratic movements like a mouse
		num_moves = max(15, int(30 * intensity))
		last_x, last_y = start_x, start_y
		
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
	
	def _execute_stalking_prey(self, start_x, start_y, intensity):
		"""Execute stalking prey pattern (slow movement followed by quick dart).
		
		Args:
			start_x: Starting X coordinate
			start_y: Starting Y coordinate
			intensity: Pattern intensity (0.1-1.0)
		"""
		last_x, last_y = start_x, start_y
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
	
	def _execute_hiding_prey(self, start_x, start_y, intensity):
		"""Execute hiding prey pattern (stop and go).
		
		Args:
			start_x: Starting X coordinate
			start_y: Starting Y coordinate
			intensity: Pattern intensity (0.1-1.0)
		"""
		last_x, last_y = start_x, start_y
		num_sequences = max(4, int(8 * intensity))
		
		for seq in range(num_sequences):
			# Hold still (but not longer than 1 second)
			freeze_time = random.uniform(0.3, 0.7)
			
			# Log the freeze 
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
	
	def _execute_fleeing_prey(self, start_x, start_y, intensity):
		"""Execute fleeing prey pattern (quick directional movements).
		
		Args:
			start_x: Starting X coordinate
			start_y: Starting Y coordinate
			intensity: Pattern intensity (0.1-1.0)
		"""
		last_x, last_y = start_x, start_y
		
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
