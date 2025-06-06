"""
Fixed Points Pattern for PetCube Helper

Moves between predefined points in a specific sequence.
"""

from .base_pattern import BasePattern


class FixedPointsPattern(BasePattern):
    """Executes a fixed pattern of touch points."""
    
    def get_name(self) -> str:
        return "Fixed Points"
    
    def get_description(self) -> str:
        return "Moves between predefined points in sequence"
    
    def _setup_commands(self):
        """Setup fixed points pattern commands."""
        # Define fixed points (relative to safe zone)
        points = [
            (0.2, 0.3),  # Top-left
            (0.5, 0.2),  # Top-center
            (0.8, 0.3),  # Top-right
            (0.8, 0.7),  # Bottom-right
            (0.5, 0.8),  # Bottom-center
            (0.2, 0.7),  # Bottom-left
        ]
        
        # Move through points in sequence
        for x, y in points:
            self.move_to(x, y, relative=True)
            self.wait(1)
        
        # Return to center
        self.move_to(0.5, 0.5, relative=True)
        self.wait(1.5)
