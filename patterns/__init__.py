"""
Patterns Package for PetCube Helper

This package contains all the pattern implementations.
"""

from .base_pattern import BasePattern, PatternCommand
from .circular_pattern import CircularPattern
from .random_pattern import RandomPattern
from .laser_pointer_pattern import LaserPointerPattern
from .fixed_points_pattern import FixedPointsPattern
from .kitty_mode_pattern import KittyModePattern

# Pattern registry
PATTERN_CLASSES = {
    "Circular": CircularPattern,
    "Random": RandomPattern,
    "Laser Pointer": LaserPointerPattern,
    "Fixed Points": FixedPointsPattern,
    "Kitty Mode": KittyModePattern,
}

__all__ = [
    "BasePattern",
    "PatternCommand",
    "CircularPattern",
    "RandomPattern",
    "LaserPointerPattern", 
    "FixedPointsPattern",
    "KittyModePattern",
    "PATTERN_CLASSES",
]
