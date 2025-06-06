"""
Random Pattern for PetCube Helper

Creates random movement patterns within the safe zone.
"""

import random
from .base_pattern import BasePattern


class RandomPattern(BasePattern):
    """Executes a random touch pattern."""
    
    def get_name(self) -> str:
        return "Random"
    
    def get_description(self) -> str:
        return "Moves the laser pointer to random positions"
    
    def _setup_commands(self):
        """Setup random pattern commands."""
        # Number of random movements
        num_moves = 8
        
        for i in range(num_moves):
            # Generate random position within safe zone
            x = random.uniform(0.1, 0.9)
            y = random.uniform(0.1, 0.9)
            
            # Move to random position
            self.move_to(x, y, relative=True)
            
            # Random wait time (0.5 to 2 time units)
            self.wait(random.uniform(0.5, 2))
