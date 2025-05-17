"""
Cat Detector Module for PetCube Helper

This module provides cat detection capabilities using computer vision.
"""

import cv2
import numpy as np
import time
import os
import threading
from pathlib import Path

class CatDetector:
    def __init__(self, adb_utility, logger=None):
        """Initialize the cat detector.
        
        Args:
            adb_utility: ADBUtility instance for interacting with the device
            logger: Function to use for logging messages
        """
        self.adb = adb_utility
        self.logger = logger or (lambda msg: print(msg))
        
        # Detection parameters
        self.detection_interval = 0.5  # seconds between detections
        self.last_detection_time = 0
        self.confidence_threshold = 0.5
        self.detection_active = False
        self.detection_thread = None
        
        # Cat tracking data
        self.cat_positions = []
        self.max_positions = 10  # Maximum number of positions to track
        self.last_detection = None  # Last detection result (x, y, w, h)
        
        # Ensure temp directory exists
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Model will be loaded when needed
        self.model = None
        self.classes = None
    
    def log(self, message):
        """Log a message using the provided logger function."""
        self.logger(message)

    def _load_model(self):
        """Load the detection model."""
        try:
            # Check if model files exist in expected locations
            model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
            
            # For now, using the default OpenCV DNN face detector as a placeholder
            # This will be replaced with a proper cat detector model later
            prototxt_path = os.path.join(cv2.__path__[0], 'data', 'haarcascade_frontalcatface.xml')
            
            # If cat model isn't available, fall back to a general model
            if not os.path.exists(prototxt_path):
                prototxt_path = os.path.join(cv2.__path__[0], 'data', 'haarcascade_frontalface_default.xml')
                self.log("Cat-specific model not found, using general detection model")
            else:
                self.log("Found cat detection model")
            
            self.model = cv2.CascadeClassifier(prototxt_path)
            return True
        
        except Exception as e:
            self.log(f"Error loading detection model: {str(e)}")
            return False
    
    def get_current_frame(self):
        """Capture current frame from device screenshot."""
        temp_file = os.path.join(self.temp_dir, "temp_frame.png")
        
        if self.adb.get_screenshot(temp_file):
            try:
                frame = cv2.imread(temp_file)
                if frame is not None:
                    return frame
            except Exception as e:
                self.log(f"Error reading screenshot: {str(e)}")
        
        return None
    
    def detect_cat(self, frame=None):
        """Detect cat in frame, returns (x, y, w, h) or None."""
        current_time = time.time()
        
        # Limit detection frequency
        if current_time - self.last_detection_time < self.detection_interval:
            return self.last_detection
        
        # Get current frame if not provided
        if frame is None:
            frame = self.get_current_frame()
            if frame is None:
                return None
        
        # Load model if needed
        if self.model is None:
            if not self._load_model():
                return None
        
        try:
            # Convert to grayscale for Haar cascade
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect cats using the cascade classifier
            detections = self.model.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Update detection time
            self.last_detection_time = current_time
            
            # Process detections
            if len(detections) > 0:
                # Take the largest detection as our cat
                areas = [w * h for (x, y, w, h) in detections]
                max_idx = areas.index(max(areas))
                cat_rect = detections[max_idx]
                
                # Update position history
                self.cat_positions.append(cat_rect)
                if len(self.cat_positions) > self.max_positions:
                    self.cat_positions.pop(0)
                
                self.last_detection = cat_rect
                return cat_rect
        
        except Exception as e:
            self.log(f"Error in cat detection: {str(e)}")
        
        return None
    
    def get_cat_position(self):
        """Get the most recent cat position."""
        return self.last_detection
    
    def get_cat_movement_vector(self):
        """Calculate cat movement vector based on recent positions.
        
        Returns:
            tuple: (dx, dy) representing movement direction, or None if insufficient data
        """
        if len(self.cat_positions) < 2:
            return None
        
        # Get the two most recent positions
        x1, y1, w1, h1 = self.cat_positions[-2]
        x2, y2, w2, h2 = self.cat_positions[-1]
        
        # Calculate center points
        center1 = (x1 + w1//2, y1 + h1//2)
        center2 = (x2 + w2//2, y2 + h2//2)
        
        # Calculate movement vector
        dx = center2[0] - center1[0]
        dy = center2[1] - center1[1]
        
        return (dx, dy)
    
    def start_detection(self):
        """Start continuous cat detection in a background thread."""
        if self.detection_active:
            return
        
        self.detection_active = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        self.log("Cat detection started")
    
    def stop_detection(self):
        """Stop the detection thread."""
        self.detection_active = False
        if self.detection_thread:
            self.detection_thread.join(timeout=1.0)
            self.detection_thread = None
        self.log("Cat detection stopped")
    
    def _detection_loop(self):
        """Background thread for continuous detection."""
        while self.detection_active:
            self.detect_cat()
            time.sleep(0.1)  # Small sleep to prevent CPU overuse
    
    def save_debug_frame(self, frame=None, show_detection=True):
        """Save a debug frame with detection visualization."""
        if frame is None:
            frame = self.get_current_frame()
            if frame is None:
                return False
        
        # Create a copy for drawing
        debug_frame = frame.copy()
        
        # Draw detection rectangle if available and requested
        if show_detection and self.last_detection is not None:
            x, y, w, h = self.last_detection
            cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Label the detection
            cv2.putText(debug_frame, "Cat", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Save the debug frame
        debug_path = os.path.join(self.temp_dir, f"cat_detection_{int(time.time())}.png")
        cv2.imwrite(debug_path, debug_frame)
        
        return True
