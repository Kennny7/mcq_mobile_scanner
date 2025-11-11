# mobile_camera.py
from kivy.uix.camera import Camera
from kivy.clock import Clock
import time
from utils.logger import app_logger
from utils.config import MobileConfig

class MobileCameraController:
    def __init__(self):
        self.camera = None
        self.is_camera_available = False
        self.last_stable_time = 0
        self.current_frame = None
        self.frame_counter = 0
        self.is_processing = False
        
        app_logger.info("MobileCameraController initialized")
    
    def initialize_camera(self):
        """Initialize mobile camera with error handling"""
        try:
            from kivy.uix.camera import Camera
            
            self.camera = Camera(
                resolution=MobileConfig.CAMERA_RESOLUTION,
                play=True
            )
            self.is_camera_available = True
            app_logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            app_logger.error(f"Camera initialization failed: {str(e)}")
            self.is_camera_available = False
            return False
    
    def capture_frame(self):
        """Capture frame from camera with performance optimization"""
        if not self.is_camera_available or self.is_processing:
            return None
        
        # Skip frames for performance
        self.frame_counter += 1
        if self.frame_counter % MobileConfig.FRAME_SKIP_COUNT != 0:
            return None
        
        try:
            if self.camera and self.camera.texture:
                self.current_frame = self.camera.texture
                return self.current_frame
        except Exception as e:
            app_logger.error(f"Frame capture error: {str(e)}")
        
        return None
    
    def check_stability(self):
        """Check if camera is stable for processing"""
        current_time = time.time()
        
        # Simulate stability check (in real app, compare frames)
        if current_time - self.last_stable_time > MobileConfig.STABLE_TIME_THRESHOLD:
            self.last_stable_time = current_time
            app_logger.info("Camera stability detected - ready for processing")
            return True
        
        return False
    
    def stop_camera(self):
        """Stop camera and cleanup"""
        if self.camera:
            self.camera.play = False
            self.is_camera_available = False
            app_logger.info("Camera stopped")