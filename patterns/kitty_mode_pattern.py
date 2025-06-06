"""
Kitty Mode Pattern for PetCube Helper

Special patterns optimized for cat engagement with prey-like movements.
"""

import random
import math
from .base_pattern import BasePattern


class KittyModePattern(BasePattern):
    """Executes patterns optimized for cat engagement."""
    
    def get_name(self) -> str:
        return "Kitty Mode"
    
    def get_description(self) -> str:
        return "Special movements designed to engage cats"
    
    def _setup_commands(self):
        """Setup kitty mode pattern commands."""
        # Randomly choose a prey behavior
        behaviors = [
            self._prey_movement,
            self._stalking_prey,
            self._hiding_prey,
            self._fleeing_prey
        ]
        
        behavior = random.choice(behaviors)
        behavior()
    
    def _prey_movement(self):
        """Small, erratic movements like a mouse."""
        # Start position
        x, y = random.uniform(0.3, 0.7), random.uniform(0.3, 0.7)
        self.move_to(x, y, relative=True)
        self.wait(0.3)
        
        # Small erratic movements
        for _ in range(15):
            # Small movement in random direction
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.02, 0.08)
            
            x += distance * math.cos(angle)
            y += distance * math.sin(angle)
            
            # Keep in bounds
            x = max(0.1, min(0.9, x))
            y = max(0.1, min(0.9, y))
            
            self.move_to(x, y, relative=True)
            self.wait(random.uniform(0.1, 0.3))
    
    def _stalking_prey(self):
        """Slow movement followed by quick dart."""
        x, y = random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)
        self.move_to(x, y, relative=True)
        
        for _ in range(3):
            # Slow stalking movements
            for _ in range(4):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0.01, 0.03)
                
                x += distance * math.cos(angle)
                y += distance * math.sin(angle)
                
                x = max(0.1, min(0.9, x))
                y = max(0.1, min(0.9, y))
                
                self.move_to(x, y, relative=True)
                self.wait(0.5)
            
            # Quick dart!
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.2, 0.4)
            
            x += distance * math.cos(angle)
            y += distance * math.sin(angle)
            
            x = max(0.1, min(0.9, x))
            y = max(0.1, min(0.9, y))
            
            self.move_to(x, y, relative=True)
            self.wait(0.1)
    
    def _hiding_prey(self):
        """Stop and go pattern."""
        x, y = random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)
        self.move_to(x, y, relative=True)
        
        for _ in range(5):
            # Hide (stay still with tiny movements)
            for _ in range(3):
                # Tiny jitter
                jitter_x = x + random.uniform(-0.01, 0.01)
                jitter_y = y + random.uniform(-0.01, 0.01)
                self.move_to(jitter_x, jitter_y, relative=True)
                self.wait(0.2)
            
            # Dash away!
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.15, 0.35)
            
            x += distance * math.cos(angle)
            y += distance * math.sin(angle)
            
            x = max(0.1, min(0.9, x))
            y = max(0.1, min(0.9, y))
            
            self.move_to(x, y, relative=True)
            self.wait(0.2)
    
    def _fleeing_prey(self):
        """Quick directional movements."""
        x, y = random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)
        self.move_to(x, y, relative=True)
        
        # Choose a general direction
        main_angle = random.uniform(0, 2 * math.pi)
        
        for _ in range(8):
            # Move in generally the same direction with variation
            angle = main_angle + random.uniform(-0.5, 0.5)
            distance = random.uniform(0.08, 0.15)
            
            x += distance * math.cos(angle)
            y += distance * math.sin(angle)
            
            # Bounce off edges
            if x < 0.1 or x > 0.9:
                main_angle = math.pi - main_angle
                x = max(0.1, min(0.9, x))
            if y < 0.1 or y > 0.9:
                main_angle = -main_angle
                y = max(0.1, min(0.9, y))
            
            self.move_to(x, y, relative=True)
            self.wait(random.uniform(0.2, 0.4))
