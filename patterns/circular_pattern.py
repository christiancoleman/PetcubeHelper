"""
Circular Pattern for PetCube Helper

Creates a circular movement pattern.
"""

import math
from .base_pattern import BasePattern


class CircularPattern(BasePattern):
    """Executes a circular touch pattern."""
    
    def get_name(self) -> str:
        return "Circular"
    
    def get_description(self) -> str:
        return "Moves the laser pointer in a circular pattern"
    
    def _setup_commands(self):
        """Setup circular pattern commands."""
        # Number of points around the circle
        num_points = 12
        
        # Center of the pattern (relative to safe zone)
        center_x, center_y = 0.5, 0.5
        radius = 0.4  # 40% of safe zone size
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Move to point on circle
            self.move_to(x, y, relative=True)
            
            # Wait a fraction of a time unit
            self.wait(0.5)
        
        # Complete the circle
        self.move_to(center_x + radius, center_y, relative=True)
        self.wait(1)
