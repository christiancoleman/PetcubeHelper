"""
Cat Reactive Patterns Module for PetCube Helper

This module implements laser patterns that react to cat position and behavior.
"""

import random
import math
import time

class CatReactivePatterns:
	def __init__(self, pattern_executor, cat_detector, logger=None):
		"""Initialize cat-reactive pattern generator.
		
		Args:
			pattern_executor: PatternExecutor instance to execute taps
			cat_detector: CatDetector instance for cat position data
			logger: Function to use for logging messages
		"""
		self.pattern_executor = pattern_executor
		self.cat_detector = cat_detector
		self.logger = logger or (lambda msg: print(msg))
		
		# Pattern configuration
		self.lead_distance = 150  # Pixels to lead the cat
		self.tease_distance = 200  # Distance to stay away when teasing
		
	def log(self, message):
		"""Log a message using the provided logger function."""
		self.logger(message)
		
	def execute_cat_following_pattern(self, intensity=0.5):
		"""Execute a pattern that moves just ahead of the cat's path.
		
		Args:
			intensity: Pattern intensity (0.1-1.0)
			
		Returns:
			bool: True if pattern executed successfully
		"""
		self.log("Executing cat-following pattern...")
		
		# Get current cat position
		cat_pos = self.cat_detector.get_cat_position()
		if not cat_pos:
			self.log("No cat detected, using fallback pattern")
			return self.pattern_executor.execute_kitty_mode_pattern(intensity)
		
		# Get cat movement vector
		movement = self.cat_detector.get_cat_movement_vector()
		
		# Number of moves based on intensity
		num_moves = max(6, int(12 * intensity))
		
		# Extract cat position
		x, y, w, h = cat_pos
		cat_center_x = x + w//2
		cat_center_y = y + h//2
		
		# Base position ahead of cat
		if movement:
			dx, dy = movement
			# Normalize movement vector
			magnitude = math.sqrt(dx*dx + dy*dy)
			if magnitude > 0:
				dx, dy = dx/magnitude, dy/magnitude
				
				# Position laser ahead of cat's movement
				lead_x = cat_center_x + int(dx * self.lead_distance)
				lead_y = cat_center_y + int(dy * self.lead_distance)
			else:
				# No significant movement, position near cat
				lead_x = cat_center_x + random.randint(-100, 100)
				lead_y = cat_center_y + random.randint(-100, 100)
		else:
			# No movement data, position near cat
			lead_x = cat_center_x + random.randint(-100, 100)
			lead_y = cat_center_y + random.randint(-100, 100)
		
		# Execute pattern around lead position
		for i in range(num_moves):
			# Random movement around lead position
			variation = 50 * intensity
			tap_x = lead_x + random.randint(-int(variation), int(variation))
			tap_y = lead_y + random.randint(-int(variation), int(variation))
			
			# Execute tap
			self.pattern_executor.execute_tap(tap_x, tap_y, f"Cat-following tap {i+1}/{num_moves}")
			
			# Delay between taps (shorter with higher intensity)
			delay = max(0.1, 0.5 * (1.0 - intensity))
			time.sleep(delay)
			
			# Recalculate lead position periodically
			if i % 3 == 0:
				cat_pos = self.cat_detector.get_cat_position()
				if cat_pos:
					x, y, w, h = cat_pos
					cat_center_x = x + w//2
					cat_center_y = y + h//2
					
					movement = self.cat_detector.get_cat_movement_vector()
					if movement:
						dx, dy = movement
						magnitude = math.sqrt(dx*dx + dy*dy)
						if magnitude > 0:
							dx, dy = dx/magnitude, dy/magnitude
							lead_x = cat_center_x + int(dx * self.lead_distance)
							lead_y = cat_center_y + int(dy * self.lead_distance)
		
		return True
		
	def execute_cat_teasing_pattern(self, intensity=0.5):
		"""Execute a pattern that teases the cat by moving away when approached.
		
		Args:
			intensity: Pattern intensity (0.1-1.0)
			
		Returns:
			bool: True if pattern executed successfully
		"""
		self.log("Executing cat-teasing pattern...")
		
		# Get current cat position
		cat_pos = self.cat_detector.get_cat_position()
		if not cat_pos:
			self.log("No cat detected, using fallback pattern")
			return self.pattern_executor.execute_kitty_mode_pattern(intensity)
		
		# Extract cat position
		x, y, w, h = cat_pos
		cat_center_x = x + w//2
		cat_center_y = y + h//2
		
		# Number of moves based on intensity
		num_moves = max(8, int(15 * intensity))
		
		# Start at a position away from the cat
		angle = random.uniform(0, 2 * math.pi)
		teasing_x = cat_center_x + int(math.cos(angle) * self.tease_distance)
		teasing_y = cat_center_y + int(math.sin(angle) * self.tease_distance)
		
		# Execute pattern
		for i in range(num_moves):
			# Execute tap
			self.pattern_executor.execute_tap(teasing_x, teasing_y, f"Cat-teasing tap {i+1}/{num_moves}")
			
			# Get updated cat position
			new_cat_pos = self.cat_detector.get_cat_position()
			if new_cat_pos:
				nx, ny, nw, nh = new_cat_pos
				new_cat_center_x = nx + nw//2
				new_cat_center_y = ny + nh//2
				
				# Calculate vector from cat to current position
				dx = teasing_x - new_cat_center_x
				dy = teasing_y - new_cat_center_y
				
				# Calculate distance
				distance = math.sqrt(dx*dx + dy*dy)
				
				# If cat is getting too close, move away
				if distance < self.tease_distance:
					# Normalize direction vector
					if distance > 0:
						dx, dy = dx/distance, dy/distance
					else:
						dx, dy = 1, 0  # Default direction if at same position
					
					# Move away from cat
					teasing_x = new_cat_center_x + int(dx * self.tease_distance)
					teasing_y = new_cat_center_y + int(dy * self.tease_distance)
				else:
					# Small random movement
					variation = 30 * intensity
					teasing_x += random.randint(-int(variation), int(variation))
					teasing_y += random.randint(-int(variation), int(variation))
			
			# Delay between taps (shorter with higher intensity)
			delay = max(0.1, 0.3 * (1.0 - intensity))
			time.sleep(delay)
		
		return True
	
	def execute_cat_enrichment_pattern(self, intensity=0.5):
		"""Execute a pattern around the cat to encourage play without direct targeting.
		
		Args:
			intensity: Pattern intensity (0.1-1.0)
			
		Returns:
			bool: True if pattern executed successfully
		"""
		self.log("Executing cat-enrichment pattern...")
		
		# Get current cat position
		cat_pos = self.cat_detector.get_cat_position()
		if not cat_pos:
			self.log("No cat detected, using fallback pattern")
			return self.pattern_executor.execute_kitty_mode_pattern(intensity)
		
		# Extract cat position
		x, y, w, h = cat_pos
		cat_center_x = x + w//2
		cat_center_y = y + h//2
		
		# Number of moves based on intensity
		num_moves = max(10, int(20 * intensity))
		
		# Create a pattern around the cat
		for i in range(num_moves):
			# Choose a random angle and distance
			angle = random.uniform(0, 2 * math.pi)
			min_distance = 50  # Don't go too close to the cat
			max_distance = 200 + (100 * intensity)  # Further with higher intensity
			distance = random.uniform(min_distance, max_distance)
			
			# Calculate position
			tap_x = cat_center_x + int(math.cos(angle) * distance)
			tap_y = cat_center_y + int(math.sin(angle) * distance)
			
			# Execute tap
			self.pattern_executor.execute_tap(tap_x, tap_y, f"Cat-enrichment tap {i+1}/{num_moves}")
			
			# Delay between taps (varied based on intensity)
			if random.random() < 0.3:
				# Occasional pause to entice cat
				delay = max(0.3, 0.8 * (1.0 - intensity))
			else:
				# Normal movement
				delay = max(0.1, 0.4 * (1.0 - intensity))
			
			time.sleep(delay)
			
			# Periodically update cat position
			if i % 3 == 0:
				new_cat_pos = self.cat_detector.get_cat_position()
				if new_cat_pos:
					x, y, w, h = new_cat_pos
					cat_center_x = x + w//2
					cat_center_y = y + h//2
		
		return True
