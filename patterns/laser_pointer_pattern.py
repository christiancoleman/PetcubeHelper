"""
Laser Pointer Pattern for PetCube Helper

Simulates realistic laser pointer movements with quick darts and smooth tracking.
"""

import random
import math
from .base_pattern import BasePattern


class LaserPointerPattern(BasePattern):
    """Executes a laser pointer-like pattern."""
    
    def get_name(self) -> str:
        return "Laser Pointer"
    
    def get_description(self) -> str:
        return "Simulates realistic laser pointer movements"
    
    def _setup_commands(self):
        """Setup laser pointer pattern commands."""
        # Start at a random position
        last_x = random.uniform(0.2, 0.8)
        last_y = random.uniform(0.2, 0.8)
        
        self.move_to(last_x, last_y, relative=True)
        self.wait(0.5)
        
        # Number of movements
        num_moves = 10
        
        for i in range(num_moves):
            if random.random() < 0.3:
                # Quick dart movement (30% chance)
                new_x = random.uniform(0.1, 0.9)
                new_y = random.uniform(0.1, 0.9)
                
                # Quick move with short wait
                self.move_to(new_x, new_y, relative=True)
                self.wait(0.2)
            else:
                # Smooth tracking movement
                # Move in a direction from last position
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0.1, 0.3)
                
                new_x = last_x + distance * math.cos(angle)
                new_y = last_y + distance * math.sin(angle)
                
                # Clamp to valid range
                new_x = max(0.1, min(0.9, new_x))
                new_y = max(0.1, min(0.9, new_y))
                
                # Smooth move with longer wait
                self.move_to(new_x, new_y, relative=True)
                self.wait(random.uniform(0.5, 1.0))
            
            last_x, last_y = new_x, new_y
