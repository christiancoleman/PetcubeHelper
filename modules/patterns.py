"""
Patterns Module for PetCube Helper

This module contains the pattern executor that manages and runs different
touch patterns using the new time-unit based pattern system.
"""

import random
import time
from patterns import PATTERN_CLASSES


class PatternExecutor:
    def __init__(self, adb_utility, logger=None, cat_detector=None):
        """Initialize the pattern executor.
        
        Args:
            adb_utility: ADBUtility instance for interacting with the device
            logger: Function to use for logging messages
            cat_detector: Optional CatDetector instance for cat-reactive patterns
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
        
        # Pattern settings
        self.time_unit_ms = 1000  # Default 1 second per time unit
        
        # Cat detection integration
        self.cat_detector = cat_detector
        self.cat_reactive_patterns = None
        
        if self.cat_detector:
            # Import here to avoid circular imports
            from modules.vision.cat_patterns import CatReactivePatterns
            self.cat_reactive_patterns = CatReactivePatterns(self, self.cat_detector, logger)
        
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
    
    def set_time_unit(self, milliseconds):
        """Set the duration of one time unit for patterns.
        
        Args:
            milliseconds: Duration of one time unit in milliseconds
        """
        self.time_unit_ms = milliseconds
        self.log(f"Time unit set to {milliseconds}ms")
    
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
            # Check if it's a cat-reactive pattern
            if pattern_type in ["Cat Following", "Cat Teasing", "Cat Enrichment"] and self.cat_reactive_patterns:
                if pattern_type == "Cat Following":
                    self.cat_reactive_patterns.execute_cat_following_pattern(intensity)
                elif pattern_type == "Cat Teasing":
                    self.cat_reactive_patterns.execute_cat_teasing_pattern(intensity)
                elif pattern_type == "Cat Enrichment":
                    self.cat_reactive_patterns.execute_cat_enrichment_pattern(intensity)
            elif pattern_type in PATTERN_CLASSES:
                # Create and execute the pattern
                pattern_class = PATTERN_CLASSES[pattern_type]
                pattern = pattern_class(self, self.time_unit_ms)
                pattern.execute(intensity)
            else:
                self.log(f"Unknown pattern type: {pattern_type}")
                self.stop_pattern()
                return False
            
            self.stop_pattern()  # Mark pattern as inactive
            return True
        except Exception as e:
            self.log(f"Error executing pattern: {str(e)}")
            self.stop_pattern()  # Mark pattern as inactive
            return False
    
    def set_cat_detector(self, cat_detector):
        """Set a cat detector for cat-reactive patterns.
        
        Args:
            cat_detector: CatDetector instance
        """
        self.cat_detector = cat_detector
        
        # Create cat reactive patterns
        if self.cat_detector:
            # Import here to avoid circular imports
            from modules.vision.cat_patterns import CatReactivePatterns
            self.cat_reactive_patterns = CatReactivePatterns(self, self.cat_detector, self.logger)
