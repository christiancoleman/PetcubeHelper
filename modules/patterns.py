"""
Patterns Module for PetCube Helper

This module contains the pattern executor that manages and runs different
touch patterns using the new time-unit based pattern system.
"""

import random
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
            x = max(self.safe_zone['min_x'], min(x, self.safe_zone['max_x']))
            y = max(self.safe_zone['min_y'], min(y, self.safe_zone['max_y']))
        
        # Log the tap if message provided
        if log_message:
            self.log(f"{log_message}: ({x}, {y})")
        
        # Execute the tap
        success = self.adb.tap_screen(x, y)
        
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
    
    def execute_pattern(self, pattern_type):
        """Execute the specified pattern.
        
        Args:
            pattern_type: The pattern type to execute
            
        Returns:
            bool: True if pattern executed successfully
        """
        self.log(f"Executing {pattern_type} pattern...")
        
        try:
            # Check if it's a cat-reactive pattern
            if pattern_type in ["Cat Following", "Cat Teasing", "Cat Enrichment"] and self.cat_reactive_patterns:
                if pattern_type == "Cat Following":
                    self.cat_reactive_patterns.execute_cat_following_pattern(0.5)
                elif pattern_type == "Cat Teasing":
                    self.cat_reactive_patterns.execute_cat_teasing_pattern(0.5)
                elif pattern_type == "Cat Enrichment":
                    self.cat_reactive_patterns.execute_cat_enrichment_pattern(0.5)
            elif pattern_type in PATTERN_CLASSES:
                # Create and execute the pattern
                pattern_class = PATTERN_CLASSES[pattern_type]
                pattern = pattern_class(self, self.time_unit_ms)
                pattern.execute(0.5)
            else:
                self.log(f"Unknown pattern type: {pattern_type}")
                return False
            
            return True
        except Exception as e:
            self.log(f"Error executing pattern: {str(e)}")
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