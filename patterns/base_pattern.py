"""
Base Pattern Module for PetCube Helper

This module provides the base class for all patterns, supporting time-unit based
command sequences.
"""

import time
import abc
from typing import List, Tuple, Dict, Any


class PatternCommand:
    """Represents a single command in a pattern sequence."""
    
    def __init__(self, command_type: str, **kwargs):
        self.command_type = command_type
        self.params = kwargs
    
    def __repr__(self):
        return f"PatternCommand({self.command_type}, {self.params})"


class BasePattern(abc.ABC):
    """Base class for all pattern implementations."""
    
    def __init__(self, executor, time_unit_ms: int = 1000):
        """Initialize the base pattern.
        
        Args:
            executor: PatternExecutor instance for executing taps
            time_unit_ms: Duration of one time unit in milliseconds
        """
        self.executor = executor
        self.time_unit_ms = time_unit_ms
        self.commands = []
        self._setup_commands()
    
    @abc.abstractmethod
    def _setup_commands(self):
        """Setup the command sequence for this pattern.
        
        This method should be implemented by subclasses to define their
        specific command sequences using methods like move_to() and wait().
        """
        pass
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """Get the name of this pattern."""
        pass
    
    @abc.abstractmethod
    def get_description(self) -> str:
        """Get a description of this pattern."""
        pass
    
    def move_to(self, x: float, y: float, relative: bool = False):
        """Add a move command to the pattern.
        
        Args:
            x: X coordinate (0.0-1.0 if relative, pixels if absolute)
            y: Y coordinate (0.0-1.0 if relative, pixels if absolute)
            relative: If True, coordinates are relative to safe zone (0.0-1.0)
        """
        self.commands.append(PatternCommand("move", x=x, y=y, relative=relative))
    
    def wait(self, units: float):
        """Add a wait command to the pattern.
        
        Args:
            units: Number of time units to wait
        """
        self.commands.append(PatternCommand("wait", units=units))
    
    def tap(self, x: float, y: float, relative: bool = False):
        """Add a tap command (move without wait) to the pattern.
        
        Args:
            x: X coordinate (0.0-1.0 if relative, pixels if absolute)
            y: Y coordinate (0.0-1.0 if relative, pixels if absolute)
            relative: If True, coordinates are relative to safe zone (0.0-1.0)
        """
        self.commands.append(PatternCommand("tap", x=x, y=y, relative=relative))
    
    def set_time_unit(self, milliseconds: int):
        """Set the duration of one time unit.
        
        Args:
            milliseconds: Duration of one time unit in milliseconds
        """
        self.time_unit_ms = milliseconds
    
    def execute(self, intensity: float = 0.5):
        """Execute the pattern.
        
        Args:
            intensity: Pattern intensity (0.1-1.0) - affects speed and scale
        """
        # Speed modifier based on intensity (higher intensity = faster)
        speed_modifier = 2.0 - intensity  # 1.9 to 1.0
        
        for command in self.commands:
            if command.command_type == "move":
                self._execute_move(command, intensity)
            elif command.command_type == "tap":
                self._execute_tap(command, intensity)
            elif command.command_type == "wait":
                self._execute_wait(command, speed_modifier)
    
    def _execute_move(self, command: PatternCommand, intensity: float):
        """Execute a move command."""
        x, y = command.params['x'], command.params['y']
        
        if command.params.get('relative', False):
            # Convert relative coordinates to absolute
            safe_zone = self.executor.safe_zone
            width = safe_zone['max_x'] - safe_zone['min_x']
            height = safe_zone['max_y'] - safe_zone['min_y']
            
            # Scale movement based on intensity
            x = safe_zone['min_x'] + (x * width * intensity)
            y = safe_zone['min_y'] + (y * height * intensity)
        
        self.executor.execute_tap(int(x), int(y))
    
    def _execute_tap(self, command: PatternCommand, intensity: float):
        """Execute a tap command (same as move but named differently for clarity)."""
        self._execute_move(command, intensity)
    
    def _execute_wait(self, command: PatternCommand, speed_modifier: float):
        """Execute a wait command."""
        wait_time = (command.params['units'] * self.time_unit_ms / 1000.0) * speed_modifier
        
        # Break up long waits to maintain safety timer
        while wait_time > 0.8:
            time.sleep(0.8)
            self.executor.make_safety_movement()
            wait_time -= 0.8
        
        if wait_time > 0:
            time.sleep(wait_time)
